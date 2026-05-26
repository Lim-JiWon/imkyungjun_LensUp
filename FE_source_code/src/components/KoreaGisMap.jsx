import { useEffect, useMemo, useState } from "react";
import { GeoJSON, MapContainer, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";

const GEOJSON_CANDIDATES = [
  "/data/korea-sido.light.geojson",
  "/korea-sido.light.geojson",
  "/korea_sido.geojson",
  "/sido.geojson",
  "/vworld_sido.geojson",
];

const REGION_ALIASES = [
  { key: "서울", aliases: ["서울", "서울특별시"] },
  { key: "부산", aliases: ["부산", "부산광역시"] },
  { key: "대구", aliases: ["대구", "대구광역시"] },
  { key: "인천", aliases: ["인천", "인천광역시"] },
  { key: "광주", aliases: ["광주", "광주광역시"] },
  { key: "대전", aliases: ["대전", "대전광역시"] },
  { key: "울산", aliases: ["울산", "울산광역시"] },
  { key: "세종", aliases: ["세종", "세종특별자치시"] },
  { key: "경기", aliases: ["경기", "경기도"] },
  { key: "강원", aliases: ["강원", "강원도", "강원특별자치도"] },
  { key: "충북", aliases: ["충북", "충청북도"] },
  { key: "충남", aliases: ["충남", "충청남도"] },
  { key: "전북", aliases: ["전북", "전라북도", "전북특별자치도"] },
  { key: "전남", aliases: ["전남", "전라남도"] },
  { key: "경북", aliases: ["경북", "경상북도"] },
  { key: "경남", aliases: ["경남", "경상남도"] },
  { key: "제주", aliases: ["제주", "제주도", "제주특별자치도"] },
];

function normalizeRegionText(value) {
  return String(value ?? "")
    .replace(/\s/g, "")
    .replace(/특별자치시/g, "")
    .replace(/특별자치도/g, "")
    .replace(/특별시/g, "")
    .replace(/광역시/g, "")
    .replace(/자치도/g, "")
    .replace(/도/g, "")
    .trim();
}

function getFeatureRegionName(feature) {
  const props = feature?.properties || {};

  return (
    props.CTP_KOR_NM ||
    props.ctp_kor_nm ||
    props.SIDO_NM ||
    props.sido_nm ||
    props.SIDO_NM_KOR ||
    props.adm_nm ||
    props.adm_nm_full ||
    props.name ||
    props.NAME ||
    props.region ||
    props.region_name ||
    props.label ||
    ""
  );
}

function getItemRegionName(item) {
  if (!item || typeof item !== "object") return "";

  return (
    item._regionName ||
    item.region ||
    item.region_name ||
    item.name ||
    item.label ||
    item.sido ||
    item.city ||
    item.area ||
    item.location ||
    ""
  );
}

function getItemCount(item) {
  if (typeof item === "number") return item;

  if (!item || typeof item !== "object") return 0;

  const count = Number(
    item._count ??
      item.count ??
      item.issue_count ??
      item.complaint_count ??
      item.total_count ??
      item.value ??
      item.score ??
      0
  );

  return Number.isFinite(count) ? count : 0;
}

function toRegionKey(regionName) {
  const target = normalizeRegionText(regionName);

  if (!target) return "";

  const matched = REGION_ALIASES.find((region) => {
    return region.aliases.some((alias) => {
      const normalizedAlias = normalizeRegionText(alias);

      return (
        target === normalizedAlias ||
        target.includes(normalizedAlias) ||
        normalizedAlias.includes(target)
      );
    });
  });

  return matched?.key || "";
}

/**
 * 값 차이가 너무 클 때도 낮은 값들끼리 색 차이가 보이도록
 * 살짝 보정한 비율을 구함
 */
function getRelativeRatio(count, minCount, maxCount) {
  if (!count || count <= 0 || maxCount <= 0) return 0;

  if (maxCount === minCount) return 1;

  const linearRatio = (count - minCount) / (maxCount - minCount);
  const clamped = Math.max(0, Math.min(1, linearRatio));

  // 낮은 값들도 색 차이가 조금 더 잘 보이도록 보정
  return Math.pow(clamped, 0.65);
}

/**
 * 적은 값: 연파랑
 * 중간 값: 노랑/주황
 * 많은 값: 빨강
 */
function getColorByCount(count, minCount, maxCount) {
  if (!count || count <= 0 || maxCount <= 0) {
    return "#eef6ff";
  }

  const ratio = getRelativeRatio(count, minCount, maxCount);

  // hue 220(파랑) -> 0(빨강)
  const hue = 220 - ratio * 220;
  const saturation = 85;
  const lightness = 88 - ratio * 38;

  return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
}

function KoreaGisMap({ regionRank = [], selectedRegionKey, onSelectRegion }) {
  const [geoJsonData, setGeoJsonData] = useState(null);
  const [geoJsonError, setGeoJsonError] = useState("");

  useEffect(() => {
    let alive = true;

    async function loadGeoJson() {
      setGeoJsonError("");

      for (const url of GEOJSON_CANDIDATES) {
        try {
          const response = await fetch(url);

          if (!response.ok) {
            continue;
          }

          const data = await response.json();

          if (!alive) return;

          setGeoJsonData(data);
          return;
        } catch (error) {
          console.warn(`${url} 로드 실패`, error);
        }
      }

      if (!alive) return;

      setGeoJsonError(
        "GeoJSON 파일을 찾지 못했습니다. public/data/korea-sido.light.geojson 파일이 있는지 확인하세요."
      );
    }

    loadGeoJson();

    return () => {
      alive = false;
    };
  }, []);

  const countByRegionKey = useMemo(() => {
    const result = {};

    if (!Array.isArray(regionRank)) return result;

    regionRank.forEach((item) => {
      const regionName = getItemRegionName(item);
      const regionKey = toRegionKey(regionName);
      const count = getItemCount(item);

      if (!regionKey) return;

      result[regionKey] = (result[regionKey] || 0) + count;
    });

    return result;
  }, [regionRank]);

  const nonZeroCounts = useMemo(() => {
    return Object.values(countByRegionKey).filter((value) => value > 0);
  }, [countByRegionKey]);

  const maxCount = useMemo(() => {
    if (nonZeroCounts.length === 0) return 0;
    return Math.max(...nonZeroCounts);
  }, [nonZeroCounts]);

  const minCount = useMemo(() => {
    if (nonZeroCounts.length === 0) return 0;
    return Math.min(...nonZeroCounts);
  }, [nonZeroCounts]);

  const geoJsonRenderKey = useMemo(() => {
    return `${selectedRegionKey || "none"}-${JSON.stringify(countByRegionKey)}`;
  }, [selectedRegionKey, countByRegionKey]);

  function getFeatureStyle(feature) {
    const featureRegionName = getFeatureRegionName(feature);
    const regionKey = toRegionKey(featureRegionName);
    const count = countByRegionKey[regionKey] || 0;
    const isSelected = selectedRegionKey && regionKey === selectedRegionKey;
    const ratio = getRelativeRatio(count, minCount, maxCount);

    return {
      fillColor: getColorByCount(count, minCount, maxCount),
      weight: isSelected ? 4 : 2,
      opacity: 1,
      color: isSelected ? "#1d4ed8" : "#ffffff",
      fillOpacity: count > 0 ? 0.72 + ratio * 0.2 : 0.45,
    };
  }

  function handleEachFeature(feature, layer) {
    const featureRegionName = getFeatureRegionName(feature);
    const regionKey = toRegionKey(featureRegionName);
    const count = countByRegionKey[regionKey] || 0;

    layer.bindTooltip(
      `<strong>${regionKey || featureRegionName}</strong><br/>민원 이슈 수 ${count}건`,
      {
        sticky: true,
        direction: "top",
      }
    );

    layer.on({
      click: () => {
        if (regionKey && typeof onSelectRegion === "function") {
          onSelectRegion(regionKey);
        }
      },
      mouseover: (event) => {
        event.target.setStyle({
          weight: 4,
          color: "#2563eb",
          fillOpacity: 1,
        });
      },
      mouseout: (event) => {
        event.target.setStyle(getFeatureStyle(feature));
      },
    });
  }

  return (
    <div
      style={{
        width: "100%",
        height: "584px",
        borderRadius: "30px",
        overflow: "hidden",
        border: "1px solid rgba(191, 219, 254, 0.9)",
        background: "#dff0ff",
        position: "relative",
      }}
    >
      {geoJsonError ? (
        <div
          style={{
            height: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "24px",
            textAlign: "center",
            color: "#475569",
            fontWeight: 800,
            lineHeight: 1.6,
          }}
        >
          {geoJsonError}
        </div>
      ) : (
        <>
          <MapContainer
            center={[36.35, 127.85]}
            zoom={6.4}
            minZoom={6}
            maxZoom={9}
            scrollWheelZoom={false}
            style={{
              width: "100%",
              height: "100%",
              background: "#dff0ff",
            }}
          >
            <TileLayer
              attribution="&copy; OpenStreetMap contributors"
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              opacity={0.25}
            />

            {geoJsonData && (
              <GeoJSON
                key={geoJsonRenderKey}
                data={geoJsonData}
                style={getFeatureStyle}
                onEachFeature={handleEachFeature}
              />
            )}
          </MapContainer>

          <div
            style={{
              position: "absolute",
              left: "18px",
              bottom: "18px",
              zIndex: 500,
              background: "rgba(255,255,255,0.92)",
              padding: "10px 12px",
              borderRadius: "14px",
              boxShadow: "0 8px 20px rgba(15,23,42,0.12)",
              fontSize: "12px",
              fontWeight: 800,
              color: "#334155",
              minWidth: "180px",
            }}
          >
            <div style={{ marginBottom: "8px" }}>민원 이슈 수</div>
            <div
              style={{
                height: "12px",
                borderRadius: "999px",
                background:
                  "linear-gradient(to right, hsl(220, 85%, 88%), hsl(160, 85%, 78%), hsl(60, 85%, 68%), hsl(28, 85%, 60%), hsl(0, 85%, 50%))",
                border: "1px solid rgba(148,163,184,0.25)",
              }}
            />
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginTop: "6px",
              }}
            >
              <span>적음</span>
              <span>많음</span>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default KoreaGisMap;