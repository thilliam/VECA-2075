// POC-007 focal route layer. Keeps inherited VECA layers for context, while
// the candidate itself is generated only from EXP-002 elevation+slope.
state.popmode='none';state.rail=false;state.roads=false;state.transmission=false;state.rez=false;state.capital=false;
let routeEnabled=true, terrainEnabled=true, terrainMode='bands';
const MODE_COLOURS={at_grade:'#2bd9c5',embankment:'#d7c14b',cutting:'#f28c45',bridge_or_elevated:'#ef5da8',tunnel:'#8b6bd6'};
const MODE_LABELS={at_grade:'At grade',embankment:'Embankment',cutting:'Cutting',bridge_or_elevated:'Bridge / elevated',tunnel:'Tunnel'};

function routeLegendHtml(){return Object.entries(MODE_LABELS).map(([k,v])=>`<div class="legend-row"><span class="legend-swatch" style="background:${MODE_COLOURS[k]}"></span><span>${v}</span></div>`).join('')}
function routeColourExpr(){return ['match',['get','construction_mode'],'at_grade',MODE_COLOURS.at_grade,'embankment',MODE_COLOURS.embankment,'cutting',MODE_COLOURS.cutting,'bridge_or_elevated',MODE_COLOURS.bridge_or_elevated,'tunnel',MODE_COLOURS.tunnel,'#ffffff']}
function syncRoute(){if(map.getLayer('hst-route'))map.setLayoutProperty('hst-route','visibility',routeEnabled?'visible':'none')}
function terrainRasterId(mode){return `poc007-terrain-${mode}`}
function syncTerrain(){['bands','slope','elevation'].forEach(m=>{if(map.getLayer(terrainRasterId(m)))map.setLayoutProperty(terrainRasterId(m),'visibility',terrainEnabled&&terrainMode===m?'visible':'none')})}
function addTerrainBackdrop(mode){const sid=`poc007-terrain-src-${mode}`;map.addSource(sid,{type:'raster',tiles:[`../poc-006/data/tiles/${mode}/{z}/{x}/{y}.png`],tileSize:256,minzoom:6,maxzoom:9,bounds:[137.8,-39.25,154.1,-9.9]});map.addLayer({id:terrainRasterId(mode),type:'raster',source:sid,minzoom:6,layout:{visibility:mode===terrainMode?'visible':'none'},paint:{'raster-opacity':0.42,'raster-resampling':'linear'}})}
function showRouteDetail(f){const p=f.properties||{};document.getElementById('detailContent').innerHTML=`<div class="eyebrow">POC-007 · SEGMENT ${p.segment_id??'—'}</div><h2>${MODE_LABELS[p.construction_mode]||p.construction_mode||'Route segment'}</h2><dl class="detail-grid"><dt>Length</dt><dd>${p.length_km??'—'} km</dd><dt>Chainage</dt><dd>${p.chainage_start_km??'—'}–${p.chainage_end_km??'—'} km</dd><dt>Mean grade</dt><dd>${p.mean_grade_pct??'—'}%</dd><dt>Max |grade|</dt><dd>${p.max_abs_grade_pct??'—'}%</dd><dt>Ground elevation</dt><dd>${p.ground_elev_min_m??'—'}–${p.ground_elev_max_m??'—'} m</dd><dt>Mean ground elevation</dt><dd>${p.ground_elev_mean_m??'—'} m</dd><dt>Terrain slope mean</dt><dd>${p.terrain_slope_mean_deg??'—'}°</dd><dt>Terrain slope P90</dt><dd>${p.terrain_slope_p90_deg??'—'}°</dd><dt>Mean rail-vs-ground</dt><dd>${p.mean_clearance_m??'—'} m</dd><dt>Range rail-vs-ground</dt><dd>${p.min_clearance_m??'—'} to ${p.max_clearance_m??'—'} m</dd></dl><div class="section-title">Why this mode?</div><div class="interpretation">${p.reason||'Heuristic terrain/profile classification.'}</div><div class="section-title">Guardrail</div><div class="interpretation">This is a terrain-only POC. It does not include horizontal curve-radius design, geology, hydrology, land constraints, structures engineering or cost.</div>`}

map.on('load',async()=>{try{
  ['bands','slope','elevation'].forEach(addTerrainBackdrop);
  const [route,summary]=await Promise.all([j('./data/hst_terrain_segments.geojson'),j('./data/hst_terrain_summary.json')]);
  map.addSource('hst-route-src',{type:'geojson',data:route});
  map.addLayer({id:'hst-route-casing',type:'line',source:'hst-route-src',paint:{'line-color':'#101820','line-width':['interpolate',['linear'],['zoom'],4,4,9,9],'line-opacity':0.82}});
  map.addLayer({id:'hst-route',type:'line',source:'hst-route-src',paint:{'line-color':routeColourExpr(),'line-width':['interpolate',['linear'],['zoom'],4,2.5,9,6.5],'line-opacity':0.98}});
  map.on('click','hst-route',e=>{if(e.features?.[0])showRouteDetail(e.features[0])});map.on('mouseenter','hst-route',()=>map.getCanvas().style.cursor='pointer');map.on('mouseleave','hst-route',()=>map.getCanvas().style.cursor='');
  const endpoints={type:'FeatureCollection',features:[{type:'Feature',geometry:{type:'Point',coordinates:[151.2093,-33.8688]},properties:{name:'Sydney CBD'}},{type:'Feature',geometry:{type:'Point',coordinates:[144.9631,-37.8136]},properties:{name:'Melbourne CBD'}}]};
  map.addSource('hst-endpoints',{type:'geojson',data:endpoints});map.addLayer({id:'hst-endpoints-dots',type:'circle',source:'hst-endpoints',paint:{'circle-radius':7,'circle-color':'#ffffff','circle-stroke-color':'#101820','circle-stroke-width':2}});map.addLayer({id:'hst-endpoints-labels',type:'symbol',source:'hst-endpoints',layout:{'text-field':['get','name'],'text-size':13,'text-offset':[0,1.2],'text-anchor':'top'},paint:{'text-color':'#fff','text-halo-color':'#17232b','text-halo-width':2}});
  document.getElementById('routeLegend').innerHTML=routeLegendHtml();
  const shares=summary.construction_share_pct||{};document.getElementById('routeSummary').innerHTML=`<strong>${summary.path_length_km?.toLocaleString?.()||summary.path_length_km} km</strong> · ${summary.segment_count} segments<br>Max profile grade ${summary.actual_max_abs_profile_grade_pct}% / ${summary.max_grade_pct}% envelope<br>Tunnel ${shares.tunnel??0}% · bridge/elevated ${shares.bridge_or_elevated??0}% · cutting ${shares.cutting??0}%`;
  document.getElementById('buildNote').textContent=`POC-007 · terrain-only Sydney–Melbourne candidate · ${summary.path_length_km} km`;
  syncRoute();syncTerrain();
}catch(e){console.error('POC-007 route load',e);document.getElementById('routeSummary').textContent='Route derivative missing — run: python tools/build_hst_terrain_path.py';document.getElementById('buildNote').textContent='POC-007 route data missing';}});

document.getElementById('routeVisible').addEventListener('change',e=>{routeEnabled=e.target.checked;syncRoute();if(map.getLayer('hst-route-casing'))map.setLayoutProperty('hst-route-casing','visibility',routeEnabled?'visible':'none')});
document.getElementById('terrainVisible').addEventListener('change',e=>{terrainEnabled=e.target.checked;syncTerrain()});document.querySelectorAll('input[name="terrainmode"]').forEach(x=>x.addEventListener('change',e=>{terrainMode=e.target.value;syncTerrain()}));
