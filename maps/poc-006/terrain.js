let terrainMode='bands';
function terrainPaint(mode){
  if(mode==='elevation') return ['interpolate',['linear'],['get','elevation_mean_m'],0,'#f7f7f7',250,'#d9e6b8',750,'#b39b72',1500,'#8d6e63',2200,'#5d4037'];
  if(mode==='slope') return ['interpolate',['linear'],['get','slope_p90_deg'],0,'#f1f8e9',3,'#dcedc8',8,'#fff9c4',15,'#ffcc80',25,'#ef9a9a',40,'#b71c1c'];
  return ['match',['get','terrain_band'],'very_low_gradient','#e8f5e9','low_gradient','#c8e6c9','moderate_gradient','#fff59d','steep','#ffb74d','very_steep','#e57373','#bdbdbd'];
}
function setTerrainMode(mode){terrainMode=mode;if(map.getLayer('terrain-fill'))map.setPaintProperty('terrain-fill','fill-color',terrainPaint(mode));updateTerrainLegend();}
function updateTerrainLegend(){const el=document.getElementById('terrainLegend');if(!el)return;const label=terrainMode==='bands'?'P90 slope bands':terrainMode==='slope'?'P90 slope (degrees)':'Mean elevation (m)';el.textContent=`Terrain: ${label}. 10 km display cells; underlying analytical rasters remain 250 m.`;}
map.on('load',async()=>{try{const data=await j('./data/terrain_buildability.geojson');map.addSource('terrain-grid',{type:'geojson',data});map.addLayer({id:'terrain-fill',type:'fill',source:'terrain-grid',layout:{visibility:'visible'},paint:{'fill-color':terrainPaint(terrainMode),'fill-opacity':0.50,'fill-outline-color':'rgba(0,0,0,0.08)'}});map.addLayer({id:'terrain-hit',type:'fill',source:'terrain-grid',paint:{'fill-color':'rgba(0,0,0,0)','fill-opacity':0}});wireClick('terrain-hit');document.getElementById('buildNote').textContent+=` · ${data.features.length.toLocaleString()} terrain cells`;updateTerrainLegend();}catch(e){console.error('terrain layer',e);document.getElementById('terrainLegend').textContent='Terrain derivative missing — run: python tools/build_terrain_screen.py';}});
document.querySelectorAll('input[name="terrainmode"]').forEach(x=>x.addEventListener('change',e=>setTerrainMode(e.target.value)));
document.getElementById('terrainVisible').addEventListener('change',e=>{setVisible('terrain-fill',e.target.checked);setVisible('terrain-hit',e.target.checked)});
