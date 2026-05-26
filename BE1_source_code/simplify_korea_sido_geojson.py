from pathlib import Path
import json
import math


BASE_DIR = Path(__file__).resolve().parent
GIS_DIR = BASE_DIR / "cache" / "gis"

INPUT_FILE = GIS_DIR / "korea-sido.geojson"
LIGHT_OUTPUT_FILE = GIS_DIR / "korea-sido.light.geojson"
TINY_OUTPUT_FILE = GIS_DIR / "korea-sido.tiny.geojson"

# tolerance는 좌표 단위 기준이다.
# 0.005는 대략 수백 m 수준으로 경계를 단순화한다.
# 0.01은 더 많이 줄이는 발표/데모용 경량 버전이다.
LIGHT_TOLERANCE = 0.005
TINY_TOLERANCE = 0.01

# 소수점 자리 수를 줄여 파일 크기를 더 줄인다.
# 5자리면 지도 화면에서는 충분히 자연스럽다.
COORD_PRECISION = 5


def file_size_kb(path: Path) -> float:
    if not path.exists():
        return 0
    return path.stat().st_size / 1024


def point_line_distance(point, start, end):
    px, py = point
    sx, sy = start
    ex, ey = end

    dx = ex - sx
    dy = ey - sy

    if dx == 0 and dy == 0:
        return math.dist(point, start)

    t = ((px - sx) * dx + (py - sy) * dy) / (dx * dx + dy * dy)
    t = max(0, min(1, t))

    projection = (sx + t * dx, sy + t * dy)

    return math.dist(point, projection)


def douglas_peucker(points, tolerance):
    if len(points) <= 2:
        return points

    start = points[0]
    end = points[-1]

    max_distance = 0
    index = 0

    for i in range(1, len(points) - 1):
        distance = point_line_distance(points[i], start, end)

        if distance > max_distance:
            index = i
            max_distance = distance

    if max_distance > tolerance:
        left = douglas_peucker(points[: index + 1], tolerance)
        right = douglas_peucker(points[index:], tolerance)

        return left[:-1] + right

    return [start, end]


def round_point(point):
    return [
        round(float(point[0]), COORD_PRECISION),
        round(float(point[1]), COORD_PRECISION),
    ]


def simplify_ring(ring, tolerance):
    if not ring or len(ring) < 4:
        return ring

    # GeoJSON Polygon ring은 첫 점과 마지막 점이 같아야 한다.
    closed = ring[0] == ring[-1]

    working_ring = ring[:-1] if closed else ring
    working_ring = [tuple(point[:2]) for point in working_ring]

    if len(working_ring) < 3:
        return ring

    simplified = douglas_peucker(working_ring, tolerance)

    # 폴리곤 최소 구성 보장
    if len(simplified) < 3:
        simplified = working_ring[:3]

    rounded = [round_point(point) for point in simplified]

    # 닫힌 ring으로 복원
    if rounded[0] != rounded[-1]:
        rounded.append(rounded[0])

    return rounded


def simplify_polygon_coordinates(coordinates, tolerance):
    simplified_polygon = []

    for ring in coordinates:
        simplified_ring = simplify_ring(ring, tolerance)

        if simplified_ring and len(simplified_ring) >= 4:
            simplified_polygon.append(simplified_ring)

    return simplified_polygon


def simplify_geometry(geometry, tolerance):
    if not geometry or "type" not in geometry:
        return geometry

    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates")

    if geometry_type == "Polygon":
        return {
            "type": "Polygon",
            "coordinates": simplify_polygon_coordinates(coordinates, tolerance),
        }

    if geometry_type == "MultiPolygon":
        simplified_multi_polygon = []

        for polygon in coordinates:
            simplified_polygon = simplify_polygon_coordinates(polygon, tolerance)

            if simplified_polygon:
                simplified_multi_polygon.append(simplified_polygon)

        return {
            "type": "MultiPolygon",
            "coordinates": simplified_multi_polygon,
        }

    return geometry


def count_coordinates_in_geometry(geometry):
    if not geometry:
        return 0

    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates", [])

    if geometry_type == "Polygon":
        return sum(len(ring) for ring in coordinates)

    if geometry_type == "MultiPolygon":
        return sum(len(ring) for polygon in coordinates for ring in polygon)

    return 0


def count_total_coordinates(geojson):
    features = geojson.get("features", [])

    return sum(
        count_coordinates_in_geometry(feature.get("geometry"))
        for feature in features
    )


def simplify_geojson(input_data, tolerance):
    output_features = []

    for feature in input_data.get("features", []):
        properties = feature.get("properties", {}) or {}

        # 프론트에서 필요한 속성만 남김
        clean_properties = {
            "region": properties.get("region") or properties.get("name") or "",
            "name": properties.get("name") or properties.get("region") or "",
        }

        simplified_feature = {
            "type": "Feature",
            "properties": clean_properties,
            "geometry": simplify_geometry(feature.get("geometry"), tolerance),
        }

        output_features.append(simplified_feature)

    return {
        "type": "FeatureCollection",
        "name": "korea_sido_light",
        "features": output_features,
    }


def save_minified_geojson(path: Path, data):
    path.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def make_output(input_data, output_file: Path, tolerance: float):
    simplified = simplify_geojson(input_data, tolerance)
    save_minified_geojson(output_file, simplified)

    before_count = count_total_coordinates(input_data)
    after_count = count_total_coordinates(simplified)

    before_size = file_size_kb(INPUT_FILE)
    after_size = file_size_kb(output_file)

    print(f"\n[DONE] {output_file.name}")
    print(f"- tolerance: {tolerance}")
    print(f"- 좌표 수: {before_count:,}개 → {after_count:,}개")
    print(f"- 파일 크기: {before_size:,.1f}KB → {after_size:,.1f}KB")

    if before_count > 0:
        reduced_ratio = (1 - after_count / before_count) * 100
        print(f"- 좌표 감소율: {reduced_ratio:.1f}%")

    if before_size > 0:
        size_ratio = (1 - after_size / before_size) * 100
        print(f"- 용량 감소율: {size_ratio:.1f}%")


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"원본 GeoJSON 파일이 없습니다: {INPUT_FILE}")

    GIS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] 원본 파일: {INPUT_FILE}")
    print(f"[INFO] 원본 크기: {file_size_kb(INPUT_FILE):,.1f}KB")

    input_data = json.loads(INPUT_FILE.read_text(encoding="utf-8"))

    feature_count = len(input_data.get("features", []))
    coordinate_count = count_total_coordinates(input_data)

    print(f"[INFO] feature 수: {feature_count}")
    print(f"[INFO] 원본 좌표 수: {coordinate_count:,}개")

    make_output(input_data, LIGHT_OUTPUT_FILE, LIGHT_TOLERANCE)
    make_output(input_data, TINY_OUTPUT_FILE, TINY_TOLERANCE)

    print("\n[FRONTEND 전달 권장]")
    print("1순위: korea-sido.light.geojson")
    print("그래도 렉 걸리면: korea-sido.tiny.geojson")
    print("\n프론트에서는 파일명을 korea-sido.geojson으로 바꿔서 public/data에 넣으면 코드 수정이 적습니다.")


if __name__ == "__main__":
    main()