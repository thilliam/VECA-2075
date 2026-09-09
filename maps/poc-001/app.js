const DATA=window.VECA_MAP_DATA;
const statusColours={existing:'#82d7ff',committed:'#8be28b',planned:'#ffd166',scenario:'#f78cff'};
const map=new maplibregl.Map({container:'map',style:'https://demotiles.maplibre.org/style.json',center:[150.5,-33.5],zoom:4.2,minZoom:3,maxZoom:14});
map.addControl(new maplibregl.NavigationControl(),'bottom-right');

const enabledLayers=new Set(DATA.catalogue.filter(x=>x.default).map(x=>x.id));
const enabledStatuses=new Set(['existing','committed','planned','scenario']);
let selectedYear=2050;

function buildControls(){
 const root=document.getElementById('layerControls');
 const groups=[...new Set(DATA.catalogue.map(x=>x.group))];
 groups.forEach(group=>{
  const wrap=document.createElement('div');wrap.className='layer-group';
  wrap.innerHTML=`<div class="layer-group-title">${group}</div>`;
  DATA.catalogue.filter(x=>x.group===group).forEach(layer=>{
   const count=DATA.features[layer.id]?.features?.length||0;
   const label=document.createElement('label');label.className='check-row';
   label.innerHTML=`<input type="checkbox" data-layer="${layer.id}" ${layer.default?'checked':''}/> ${layer.label}<span class="count">${count}</span>`;
   wrap.appendChild(label);
  });
  root.appendChild(wrap);
 });
}

function visibilityFilter(layerId){
 const source=DATA.features[layerId];
 const valid=source.features.filter(f=>enabledStatuses.has(f.properties.status)&&Number(f.properties.year)<=selectedYear);
 return {type:'FeatureCollection',features:valid};
}

function addSourceAndLayers(layer){
 const id=layer.id;
 map.addSource(id,{type:'geojson',data:visibilityFilter(id)});
 const sample=DATA.features[id]?.features?.[0];if(!sample)return;
 const type=sample.geometry.type;
 if(type==='Point'){
  map.addLayer({id:`${id}-halo`,type:'circle',source:id,minzoom:layer.minZoom,paint:{'circle-radius':['interpolate',['linear'],['zoom'],3,8,10,14],'circle-color':'#0d141a','circle-opacity':0.82}});
  map.addLayer({id,type:'circle',source:id,minzoom:layer.minZoom,paint:{'circle-radius':['interpolate',['linear'],['zoom'],3,4,10,8],'circle-color':['match',['get','status'],'existing',statusColours.existing,'committed',statusColours.committed,'planned',statusColours.planned,'scenario',statusColours.scenario,'#fff'],'circle-stroke-color':'#0d141a','circle-stroke-width':1.5}});
  map.addLayer({id:`${id}-labels`,type:'symbol',source:id,minzoom:Math.max(layer.minZoom+1,5),layout:{'text-field':['get','name'],'text-size':11,'text-offset':[0,1.2],'text-anchor':'top','text-allow-overlap':false},paint:{'text-color':'#f2f6f8','text-halo-color':'#111b22','text-halo-width':1.5}});
 }else if(type==='LineString'){
  const isScenario=id==='scenario';
  map.addLayer({id:`${id}-halo`,type:'line',source:id,minzoom:layer.minZoom,paint:{'line-color':'#0b1116','line-width':['interpolate',['linear'],['zoom'],3,5,10,9],'line-opacity':0.8}});
  const paint={
   'line-color':isScenario?statusColours.scenario:statusColours.existing,
   'line-width':['interpolate',['linear'],['zoom'],3,3,10,6],
   'line-opacity':0.98
  };
  if(isScenario)paint['line-dasharray']=[2,2];
  map.addLayer({id,type:'line',source:id,minzoom:layer.minZoom,paint});
 }
 setLayerVisibility(id,enabledLayers.has(id));
}

function layerIds(id){return [id,`${id}-halo`,`${id}-labels`].filter(x=>map.getLayer(x));}
function setLayerVisibility(id,on){layerIds(id).forEach(x=>map.setLayoutProperty(x,'visibility',on?'visible':'none'))}
function refreshData(){DATA.catalogue.forEach(l=>{const s=map.getSource(l.id);if(s)s.setData(visibilityFilter(l.id));});}

function showDetail(feature){
 const p=feature.properties;
 const panel=document.getElementById('detailPanel');panel.classList.remove('empty');
 document.getElementById('detailContent').innerHTML=`
  <div class="eyebrow">${(p.region||'VECA').toUpperCase()}</div>
  <h2>${p.name}</h2>
  <div><span class="tag">${p.status}</span><span class="tag">${p.layer}</span></div>
  <dl class="detail-grid"><dt>ID</dt><dd>${p.id}</dd><dt>Jurisdiction</dt><dd>${p.jurisdiction||'—'}</dd><dt>Visible by</dt><dd>${p.year||'—'}</dd><dt>Role</dt><dd>${p.role||'—'}</dd></dl>
  <div class="section-title">VECA interpretation</div><div class="interpretation">${p.interpretation||'No interpretation recorded.'}</div>
  ${p.source?`<a class="source-link" target="_blank" rel="noopener" href="${p.source}">Open source / evidence ↗</a>`:''}`;
}

function wireLayerClicks(id){
 layerIds(id).forEach(layerId=>{
  if(layerId.endsWith('-labels')||layerId.endsWith('-halo'))return;
  map.on('click',layerId,e=>{if(e.features?.[0])showDetail(e.features[0]);});
  map.on('mouseenter',layerId,()=>map.getCanvas().style.cursor='pointer');
  map.on('mouseleave',layerId,()=>map.getCanvas().style.cursor='');
 });
}

buildControls();
map.on('load',()=>{DATA.catalogue.forEach(addSourceAndLayers);DATA.catalogue.forEach(l=>wireLayerClicks(l.id));});

document.getElementById('layerControls').addEventListener('change',e=>{const id=e.target.dataset.layer;if(!id)return;e.target.checked?enabledLayers.add(id):enabledLayers.delete(id);setLayerVisibility(id,e.target.checked);});
document.querySelectorAll('[data-status]').forEach(el=>el.addEventListener('change',e=>{const s=e.target.dataset.status;e.target.checked?enabledStatuses.add(s):enabledStatuses.delete(s);refreshData();}));
document.getElementById('year').addEventListener('input',e=>{selectedYear=Number(e.target.value);document.getElementById('yearLabel').textContent=selectedYear;refreshData();});
document.getElementById('resetView').addEventListener('click',()=>map.flyTo({center:[150.5,-33.5],zoom:4.2}));
document.querySelectorAll('[data-jump]').forEach(el=>el.addEventListener('click',()=>{const j=DATA.jumps[el.dataset.jump];map.flyTo({...j,duration:900});}));
document.getElementById('closeDetail').addEventListener('click',()=>document.getElementById('detailPanel').classList.add('empty'));
