state.popmode='none';state.rail=false;state.roads=false;state.transmission=false;state.rez=false;state.capital=false;
let terrainMode='bands',terrainEnabled=true,terrainCellCount=0;
const terrainBounds=[137.8,-39.25,154.1,-9.9];
function terrainPaint(mode){
  if(mode==='elevation') return ['interpolate',['linear'],['get','elevation_mean_m'],0,'#f7f7f7',250,'#d9e6b8',750,'#b39b72',1500,'#8d6e63',2200,'#5d4037'];
  if(mode==='slope') return ['interpolate',['linear'],['get','slope_p90_deg'],0,'#f1f8e9',3,'#dcedc8',8,'#fff9c4',15,'#ffcc80',25,'#ef9a9a',40,'#b71c1c'];
  return ['match',['get','terrain_band'],'very_low_gradient','#e8f5e9','low_gradient','#c8e6c9','moderate_gradient','#fff59d','steep','#ffb74d','very_steep','#e57373','#bdbdbd'];
}
function rasterId(mode){return `terrain-detail-${mode}`;}
function syncTerrainLayers(){
  if(map.getLayer('terrain-fill'))map.setLayoutProperty('terrain-fill','visibility',terrainEnabled?'visible':'none');
  if(map.getLayer('terrain-hit'))map.setLayoutProperty('terrain-hit','visibility',terrainEnabled?'visible':'none');
  ['bands','slope','elevation'].forEach(m=>{if(map.getLayer(rasterId(m)))map.setLayoutProperty(rasterId(m),'visibility',terrainEnabled&&terrainMode===m?'visible':'none')});
}
function setTerrainMode(mode){terrainMode=mode;if(map.getLayer('terrain-fill'))map.setPaintProperty('terrain-fill','fill-color',terrainPaint(mode));syncTerrainLayers();updateTerrainLegend();}
function updateTerrainLegend(){const el=document.getElementById('terrainLegend');if(!el)return;const label=terrainMode==='bands'?'slope bands':terrainMode==='slope'?'slope (degrees)':'elevation (m)';el.textContent=`Terrain: ${label}. Overview uses 10 km summary cells; zoom 6+ uses raster tiles derived from the 250 m analytical surface.`;}
function showTerrainDetail(f){const p=f.properties||{};document.getElementById('detailContent').innerHTML=`<div class="eyebrow">TERRAIN · EXP-002</div><h2>${String(p.terrain_band||'terrain').replaceAll('_',' ')}</h2><dl class="detail-grid"><dt>Mean elevation</dt><dd>${p.elevation_mean_m??'—'} m</dd><dt>Median slope</dt><dd>${p.slope_median_deg??'—'}°</dd><dt>P90 slope</dt><dd>${p.slope_p90_deg??'—'}°</dd><dt>Share >=15°</dt><dd>${p.steep_share_ge15==null?'—':(Number(p.steep_share_ge15)*100).toFixed(1)+'%'}</dd><dt>Analysis surface</dt><dd>${p.analysis_resolution_m??'—'} m</dd><dt>Overview cell</dt><dd>${p.map_cell_m??'—'} m</dd><dt>Source</dt><dd>${p.source_surface||'GA SRTM 3-second DEM'}</dd></dl><div class="section-title">Interpretation</div><div class="interpretation">The panel is the 10 km summary cell. At closer zoom the visible terrain is rendered from the 250 m analytical surface. Terrain alone is not parcel buildability, flood, geology, land-use or servicing feasibility.</div>`;}
function addTerrainRaster(mode){
  const sid=`terrain-${mode}-tiles`;
  map.addSource(sid,{type:'raster',tiles:[`./data/tiles/${mode}/{z}/{x}/{y}.png`],tileSize:256,minzoom:6,maxzoom:9,bounds:terrainBounds});
  map.addLayer({id:rasterId(mode),type:'raster',source:sid,minzoom:6,layout:{visibility:mode===terrainMode?'visible':'none'},paint:{'raster-opacity':0.72,'raster-resampling':'linear'}});
}
function setTerrainBuildNote(){if(terrainCellCount)document.getElementById('buildNote').textContent=`POC-006 terrain · ${terrainCellCount.toLocaleString()} overview cells · 250 m detail surface`;}
map.on('load',async()=>{try{
  const data=await j('./data/terrain_buildability.geojson');terrainCellCount=data.features.length;
  map.addSource('terrain-grid',{type:'geojson',data});
  map.addLayer({id:'terrain-fill',type:'fill',source:'terrain-grid',maxzoom:6.15,layout:{visibility:'visible'},paint:{'fill-color':terrainPaint(terrainMode),'fill-opacity':0.50,'fill-outline-color':'rgba(0,0,0,0.08)'}});
  map.addLayer({id:'terrain-hit',type:'fill',source:'terrain-grid',paint:{'fill-color':'rgba(0,0,0,0)','fill-opacity':0}});
  ['bands','slope','elevation'].forEach(addTerrainRaster);
  map.on('click','terrain-hit',e=>{if(e.features?.[0])showTerrainDetail(e.features[0])});map.on('mouseenter','terrain-hit',()=>map.getCanvas().style.cursor='pointer');map.on('mouseleave','terrain-hit',()=>map.getCanvas().style.cursor='');
  syncTerrainLayers();setTerrainBuildNote();updateTerrainLegend();
}catch(e){console.error('terrain layer',e);document.getElementById('terrainLegend').textContent='Terrain derivative missing — run: python tools/build_terrain_screen.py';}});
map.on('idle',()=>{const n=document.getElementById('buildNote');if(terrainCellCount&&n&&n.textContent.startsWith('Build data missing'))setTerrainBuildNote();});
document.querySelectorAll('input[name="terrainmode"]').forEach(x=>x.addEventListener('change',e=>setTerrainMode(e.target.value)));
document.getElementById('terrainVisible').addEventListener('change',e=>{terrainEnabled=e.target.checked;syncTerrainLayers()});
