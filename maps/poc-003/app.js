const map=new maplibregl.Map({container:'map',style:'https://demotiles.maplibre.org/style.json',center:[150.5,-33.5],zoom:4.2,minZoom:3,maxZoom:14});
map.addControl(new maplibregl.NavigationControl(),'bottom-right');
const jumps={sydney:{center:[150.97,-33.80],zoom:8},seq:{center:[152.4,-27.55],zoom:7},central:{center:[151.33,-33.28],zoom:8},newengland:{center:[151.15,-30.75],zoom:6.7},riverina:{center:[147.5,-35.5],zoom:6.4},gippsland:{center:[146.5,-38],zoom:7}};
const state={population:true,growth:false,settlements:true,rail:true,roads:false,landUse:false,satellite:false};

function setVisible(id,on){if(map.getLayer(id))map.setLayoutProperty(id,'visibility',on?'visible':'none')}
function addRaster(){
 map.addSource('satellite',{type:'raster',tiles:['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],tileSize:256,attribution:'Esri World Imagery'});
 map.addLayer({id:'satellite',type:'raster',source:'satellite',layout:{visibility:'none'},paint:{'raster-opacity':0.97}});
 map.addSource('landuse',{type:'raster',tiles:['https://di-daa.img.arcgis.com/arcgis/rest/services/Land_and_vegetation/NLUM_v7_1_SIMPLIFIED_2020_21/ImageServer/exportImage?bbox={bbox-epsg-3857}&bboxSR=3857&imageSR=3857&size=256%2C256&format=png32&transparent=true&f=image'],tileSize:256,attribution:'ABARES / Digital Atlas of Australia'});
 map.addLayer({id:'landuse',type:'raster',source:'landuse',layout:{visibility:'none'},paint:{'raster-opacity':0.48}});
}

function densityColour(){return ['interpolate',['linear'],['coalesce',['to-number',['get','density_2025']],0],0,'#0a1720',10,'#173a4c',100,'#277d86',500,'#e1bb62',2000,'#e56b4f',6000,'#d32929']}
function growthColour(){return ['interpolate',['linear'],['coalesce',['to-number',['get','change_2020_25_pct']],0],-10,'#5276a7',0,'#d9d9d9',10,'#e9b44c',30,'#d95f36',70,'#a20d2a']}
function addPopulation(data){
 map.addSource('population-sa2',{type:'geojson',data});
 map.addLayer({id:'population-fill',type:'fill',source:'population-sa2',paint:{'fill-color':densityColour(),'fill-opacity':0.50}});
 map.addLayer({id:'population-outline',type:'line',source:'population-sa2',minzoom:7,paint:{'line-color':'#dfe8ed','line-width':0.35,'line-opacity':0.35}});
 map.addLayer({id:'growth-fill',type:'fill',source:'population-sa2',layout:{visibility:'none'},paint:{'fill-color':growthColour(),'fill-opacity':0.58}});
 wireClick('population-fill');wireClick('growth-fill');
}
function addSettlements(data){
 map.addSource('settlements',{type:'geojson',data});
 const levels=[{r:1,z:3,s:16},{r:2,z:4,s:15},{r:3,z:5,s:14},{r:4,z:6,s:13},{r:5,z:7,s:12},{r:6,z:8,s:11}];
 levels.forEach(x=>map.addLayer({id:`settlements-r${x.r}`,type:'symbol',source:'settlements',minzoom:x.z,filter:['==',['get','settlement_rank'],x.r],layout:{'text-field':['get','name'],'text-size':x.s,'text-font':['Open Sans Bold'],'text-allow-overlap':false,'text-padding':4},paint:{'text-color':'#ffffff','text-halo-color':'#17232b','text-halo-width':2}}));
 levels.forEach(x=>wireClick(`settlements-r${x.r}`));
}
function addTransport(id,data,colour,minzoom,visible){map.addSource(id,{type:'geojson',data});map.addLayer({id,type:'line',source:id,minzoom,layout:{visibility:visible?'visible':'none'},paint:{'line-color':colour,'line-width':['interpolate',['linear'],['zoom'],4,1,10,2.5],'line-opacity':0.72}});wireClick(id)}
function wireClick(id){map.on('click',id,e=>{if(e.features?.[0])showDetail(e.features[0])});map.on('mouseenter',id,()=>map.getCanvas().style.cursor='pointer');map.on('mouseleave',id,()=>map.getCanvas().style.cursor='')}
function fmt(n){const x=Number(n);return Number.isFinite(x)?x.toLocaleString(): '—'}
function showDetail(f){const p=f.properties||{};const panel=document.getElementById('detailPanel');panel.classList.remove('empty');let body='';
 if(p.domain==='settlement')body=`<div class="eyebrow">SETTLEMENT</div><h2>${p.name}</h2><div class="metric">${p.population_2021?fmt(p.population_2021):'Functional centre'}</div><p>${p.population_2021?'2021 Census population':'VECA metropolitan sub-centre classification'}</p><dl class="detail-grid"><dt>Rank</dt><dd>${p.settlement_rank||'—'}</dd><dt>Type</dt><dd>${p.settlement_type||'—'}</dd><dt>Geometry</dt><dd>${p.geometry_quality||'—'}</dd><dt>Source</dt><dd>${p.source_dataset||'—'}</dd></dl>`;
 else if(p.domain==='population')body=`<div class="eyebrow">SA2 POPULATION</div><h2>${p.name}</h2><div class="metric">${fmt(p.erp_2025)}</div><p>Estimated residents, 2025</p><dl class="detail-grid"><dt>Density</dt><dd>${fmt(p.density_2025)} / km²</dd><dt>2020–25</dt><dd>${fmt(p.change_2020_25_abs)} (${p.change_2020_25_pct||0}%)</dd><dt>State</dt><dd>${p.state||'—'}</dd><dt>Geometry</dt><dd>${p.geometry_quality||'—'}</dd><dt>Source</dt><dd>${p.source_dataset||'—'}</dd></dl>`;
 else body=`<div class="eyebrow">${String(p.domain||'VECA').toUpperCase()}</div><h2>${p.name||p.entity_id||'Feature'}</h2><dl class="detail-grid"><dt>ID</dt><dd>${p.entity_id||'—'}</dd><dt>Source</dt><dd>${p.source_dataset||'—'}</dd></dl>`;
 document.getElementById('detailContent').innerHTML=body;
}

async function load(){try{
 const [pop,settlements,rail,roads]=await Promise.all([
  fetch('./data/population_sa2.geojson').then(r=>r.json()),fetch('./data/settlements.geojson').then(r=>r.json()),fetch('../poc-002/data/rail.geojson').then(r=>r.json()),fetch('../poc-002/data/roads.geojson').then(r=>r.json())]);
 addRaster();addPopulation(pop);addTransport('rail',rail,'#6fd8ff',4,true);addTransport('roads',roads,'#d7ba74',5,false);addSettlements(settlements);
 document.getElementById('buildNote').textContent=`POC-003 · ${pop.features.length.toLocaleString()} SA2s · ${settlements.features.length.toLocaleString()} settlements`;
}catch(e){console.error(e);document.getElementById('buildNote').textContent='Build data missing — run: python tools/build_map_poc003.py';}}
map.on('load',load);

document.querySelectorAll('input[name=base]').forEach(x=>x.addEventListener('change',e=>{state.satellite=e.target.value==='satellite';setVisible('satellite',state.satellite)}));
document.getElementById('landUse').addEventListener('change',e=>setVisible('landuse',e.target.checked));
document.getElementById('population').addEventListener('change',e=>{state.population=e.target.checked;setVisible('population-fill',state.population&&!state.growth);setVisible('population-outline',state.population)});
document.getElementById('growth').addEventListener('change',e=>{state.growth=e.target.checked;setVisible('growth-fill',state.growth);setVisible('population-fill',state.population&&!state.growth)});
document.getElementById('settlements').addEventListener('change',e=>{for(let r=1;r<=6;r++)setVisible(`settlements-r${r}`,e.target.checked)});
document.getElementById('rail').addEventListener('change',e=>setVisible('rail',e.target.checked));
document.getElementById('roads').addEventListener('change',e=>setVisible('roads',e.target.checked));
document.getElementById('east').addEventListener('click',()=>map.flyTo({center:[150.5,-33.5],zoom:4.2}));
document.querySelectorAll('[data-jump]').forEach(b=>b.addEventListener('click',()=>map.flyTo({...jumps[b.dataset.jump],duration:900})));
document.getElementById('closeDetail').addEventListener('click',()=>document.getElementById('detailPanel').classList.add('empty'));
