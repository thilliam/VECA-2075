const map=new maplibregl.Map({container:'map',style:'https://demotiles.maplibre.org/style.json',center:[150.5,-33.5],zoom:4.2,minZoom:3,maxZoom:14});
map.addControl(new maplibregl.NavigationControl(),'bottom-right');
const jumps={sydney:{center:[150.97,-33.80],zoom:8},seq:{center:[152.4,-27.55],zoom:7},central:{center:[151.33,-33.28],zoom:8},newengland:{center:[151.15,-30.75],zoom:6.7},riverina:{center:[147.5,-35.5],zoom:6.4},gippsland:{center:[146.5,-38],zoom:7}};
const state={popmode:'sa2-density',settlements:true,rail:true,roads:false,landUse:false,satellite:false};
function setVisible(id,on){if(map.getLayer(id))map.setLayoutProperty(id,'visibility',on?'visible':'none')}
function addRaster(){
 map.addSource('satellite',{type:'raster',tiles:['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],tileSize:256,attribution:'Esri World Imagery'});
 map.addLayer({id:'satellite',type:'raster',source:'satellite',layout:{visibility:'none'},paint:{'raster-opacity':0.97}});
 map.addSource('landuse',{type:'raster',tiles:['https://di-daa.img.arcgis.com/arcgis/rest/services/Land_and_vegetation/NLUM_v7_1_SIMPLIFIED_2020_21/ImageServer/exportImage?bbox={bbox-epsg-3857}&bboxSR=3857&imageSR=3857&size=256%2C256&format=png32&transparent=true&f=image'],tileSize:256,attribution:'ABARES / Digital Atlas of Australia'});
 map.addLayer({id:'landuse',type:'raster',source:'landuse',layout:{visibility:'none'},paint:{'raster-opacity':0.48}});
}
function densityColour(){return ['interpolate',['linear'],['coalesce',['to-number',['get','density_2025']],0],0,'#0a1720',10,'#173a4c',100,'#277d86',500,'#e1bb62',2000,'#e56b4f',6000,'#d32929']}
function growthColour(){return ['interpolate',['linear'],['coalesce',['to-number',['get','change_2020_25_pct']],0],-10,'#5276a7',0,'#d9d9d9',10,'#e9b44c',30,'#d95f36',70,'#a20d2a']}
function lgaPopulationColour(){return ['interpolate',['linear'],['coalesce',['to-number',['get','erp_2025']],0],0,'#14202a',25000,'#3c6f83',100000,'#72b7a1',250000,'#d6d86d',500000,'#ef9b50']}
function addPopulation(sa2,lga){
 map.addSource('population-sa2',{type:'geojson',data:sa2});
 map.addLayer({id:'sa2-density',type:'fill',source:'population-sa2',paint:{'fill-color':densityColour(),'fill-opacity':0.50}});
 map.addLayer({id:'sa2-growth',type:'fill',source:'population-sa2',layout:{visibility:'none'},paint:{'fill-color':growthColour(),'fill-opacity':0.58}});
 map.addLayer({id:'sa2-outline',type:'line',source:'population-sa2',minzoom:7,paint:{'line-color':'#dfe8ed','line-width':0.35,'line-opacity':0.3}});
 map.addSource('population-lga',{type:'geojson',data:lga});
 map.addLayer({id:'lga-population',type:'fill',source:'population-lga',layout:{visibility:'none'},paint:{'fill-color':lgaPopulationColour(),'fill-opacity':0.60}});
 map.addLayer({id:'lga-growth',type:'fill',source:'population-lga',layout:{visibility:'none'},paint:{'fill-color':growthColour(),'fill-opacity':0.62}});
 map.addLayer({id:'lga-outline',type:'line',source:'population-lga',minzoom:5,layout:{visibility:'none'},paint:{'line-color':'#6ed7ff','line-width':['interpolate',['linear'],['zoom'],5,0.7,10,1.5],'line-opacity':0.75}});
 map.addLayer({id:'lga-labels',type:'symbol',source:'population-lga',minzoom:6,layout:{visibility:'none','text-field':['get','name'],'text-size':12,'text-allow-overlap':false,'text-padding':5},paint:{'text-color':'#fff','text-halo-color':'#17232b','text-halo-width':2}});
 ['sa2-density','sa2-growth','lga-population','lga-growth','lga-labels'].forEach(wireClick);
 updatePopulationMode();
}
function updatePopulationMode(){
 const m=state.popmode; const isLga=m.startsWith('lga-');
 setVisible('sa2-density',m==='sa2-density');setVisible('sa2-growth',m==='sa2-growth');setVisible('sa2-outline',!isLga);
 setVisible('lga-population',m==='lga-population');setVisible('lga-growth',m==='lga-growth');setVisible('lga-outline',isLga);setVisible('lga-labels',isLga);
 updateLegend();
}
function addSettlements(data){
 map.addSource('settlements',{type:'geojson',data});
 const levels=[{r:1,z:3,s:16,d:10},{r:2,z:4,s:15,d:9},{r:3,z:5,s:14,d:8},{r:4,z:6,s:13,d:7},{r:5,z:7,s:12,d:6},{r:6,z:8,s:11,d:5}];
 levels.forEach(x=>{map.addLayer({id:`settlements-r${x.r}-dots`,type:'circle',source:'settlements',minzoom:x.z,filter:['==',['get','settlement_rank'],x.r],paint:{'circle-radius':x.d,'circle-color':'#fff','circle-opacity':0.92,'circle-stroke-color':'#17232b','circle-stroke-width':2}});map.addLayer({id:`settlements-r${x.r}`,type:'symbol',source:'settlements',minzoom:x.z,filter:['==',['get','settlement_rank'],x.r],layout:{'text-field':['get','name'],'text-size':x.s,'text-offset':[0,1.25],'text-anchor':'top','text-allow-overlap':false,'text-padding':3},paint:{'text-color':'#fff','text-halo-color':'#17232b','text-halo-width':2}});wireClick(`settlements-r${x.r}-dots`);wireClick(`settlements-r${x.r}`)});
}
function setSettlementsVisible(on){for(let r=1;r<=6;r++){setVisible(`settlements-r${r}`,on);setVisible(`settlements-r${r}-dots`,on)}}
function addTransport(id,data,colour,minzoom,visible){map.addSource(id,{type:'geojson',data});map.addLayer({id,type:'line',source:id,minzoom,layout:{visibility:visible?'visible':'none'},paint:{'line-color':colour,'line-width':['interpolate',['linear'],['zoom'],4,1,10,2.5],'line-opacity':0.72}});wireClick(id)}
function wireClick(id){map.on('click',id,e=>{if(e.features?.[0])showDetail(e.features[0])});map.on('mouseenter',id,()=>map.getCanvas().style.cursor='pointer');map.on('mouseleave',id,()=>map.getCanvas().style.cursor='')}
function fmt(n){const x=Number(n);return Number.isFinite(x)?x.toLocaleString(): '—'}
function showDetail(f){const p=f.properties||{};let body='';
 if(p.domain==='settlement')body=`<div class="eyebrow">SETTLEMENT</div><h2>${p.name}</h2><div class="metric">${p.population_2021?fmt(p.population_2021):'Functional centre'}</div><p>${p.population_2021?'2021 Census population':'VECA metropolitan functional centre'}</p><dl class="detail-grid"><dt>Rank</dt><dd>${p.settlement_rank||'—'}</dd><dt>Type</dt><dd>${p.settlement_type||'—'}</dd><dt>Source</dt><dd>${p.source_dataset||'—'}</dd></dl>`;
 else if(p.domain==='lga')body=`<div class="eyebrow">LGA · ADMINISTRATIVE POPULATION</div><h2>${p.name}</h2><div class="metric">${fmt(p.erp_2025)}</div><p>Estimated residents, 2025</p><dl class="detail-grid"><dt>2020–25</dt><dd>${fmt(p.change_2020_25_abs)} (${p.change_2020_25_pct||0}%)</dd><dt>2024–25</dt><dd>${fmt(p.change_2024_25_abs)} (${p.change_2024_25_pct||0}%)</dd><dt>Internal migration</dt><dd>${fmt(p.net_internal_migration_2024_25)}</dd><dt>Overseas migration</dt><dd>${fmt(p.net_overseas_migration_2024_25)}</dd><dt>Natural increase</dt><dd>${fmt(p.natural_increase_2024_25)}</dd><dt>State</dt><dd>${p.state||'—'}</dd><dt>Source</dt><dd>${p.source_dataset||'—'}</dd></dl>`;
 else if(p.domain==='population')body=`<div class="eyebrow">SA2 POPULATION</div><h2>${p.name}</h2><div class="metric">${fmt(p.erp_2025)}</div><p>Estimated residents, 2025</p><dl class="detail-grid"><dt>Density</dt><dd>${fmt(p.density_2025)} / km²</dd><dt>2020–25</dt><dd>${fmt(p.change_2020_25_abs)} (${p.change_2020_25_pct||0}%)</dd><dt>State</dt><dd>${p.state||'—'}</dd><dt>Source</dt><dd>${p.source_dataset||'—'}</dd></dl>`;
 else body=`<div class="eyebrow">${String(p.domain||'VECA').toUpperCase()}</div><h2>${p.name||p.entity_id||'Feature'}</h2>`;
 document.getElementById('detailContent').innerHTML=body;updateLegend();
}
function swatch(color,label){return `<div class="legend-row"><span class="legend-swatch" style="background:${color}"></span><span>${label}</span></div>`}
function dot(size,label){return `<div class="legend-row"><span class="legend-dot" style="width:${size}px;height:${size}px"></span><span>${label}</span></div>`}
function updateLegend(){let html='<div class="legend-title">Map legend</div>';const m=state.popmode;
 if(m==='sa2-density')html+='<div class="legend-sub">SA2 · 2025 people/km²</div>'+swatch('#0a1720','Very sparse · <10')+swatch('#173a4c','Sparse · 10–100')+swatch('#277d86','Urbanising · 100–500')+swatch('#e1bb62','Urban · 500–2,000')+swatch('#e56b4f','Dense · 2,000–6,000')+swatch('#d32929','Very dense · 6,000+');
 if(m==='sa2-growth'||m==='lga-growth')html+=`<div class="legend-sub">${m.startsWith('lga')?'LGA':'SA2'} · population growth 2020–25</div>`+swatch('#5276a7','Decline ~−10%')+swatch('#d9d9d9','Little / no change')+swatch('#e9b44c','Growth ~10%')+swatch('#d95f36','Growth ~30%')+swatch('#a20d2a','Very high growth ~70%+');
 if(m==='lga-population')html+='<div class="legend-sub">LGA · 2025 resident population</div>'+swatch('#14202a','<25k')+swatch('#3c6f83','25k–100k')+swatch('#72b7a1','100k–250k')+swatch('#d6d86d','250k–500k')+swatch('#ef9b50','500k+');
 if(state.settlements)html+='<div class="legend-divider"></div><div class="legend-sub">Settlement hierarchy</div>'+dot(18,'Rank 1 · major metropolis')+dot(16,'Rank 2 · large urban centre')+dot(14,'Rank 3 · regional / metro centre')+dot(12,'Rank 4 · town / small city')+dot(10,'Ranks 5–6 · smaller towns');
 if(state.landUse)html+='<div class="legend-divider"></div><div class="legend-sub">Land use</div><div class="note">Colours supplied by the live ABARES national land-use service.</div>';
 document.getElementById('legendPanel').innerHTML=html;
}
async function load(){try{const [sa2,lga,settlements,rail,roads]=await Promise.all([fetch('./data/population_sa2.geojson').then(r=>r.json()),fetch('./data/population_lga.geojson').then(r=>r.json()),fetch('./data/settlements.geojson').then(r=>r.json()),fetch('../poc-002/data/rail.geojson').then(r=>r.json()),fetch('../poc-002/data/roads.geojson').then(r=>r.json())]);addRaster();addPopulation(sa2,lga);addTransport('rail',rail,'#6fd8ff',4,true);addTransport('roads',roads,'#d7ba74',5,false);addSettlements(settlements);updateLegend();document.getElementById('buildNote').textContent=`POC-003 · ${sa2.features.length.toLocaleString()} SA2s · ${lga.features.length.toLocaleString()} LGAs · ${settlements.features.length.toLocaleString()} settlements`;}catch(e){console.error(e);document.getElementById('buildNote').textContent='Build data missing — run: python tools/build_map_poc003.py';}}
map.on('load',load);
document.querySelectorAll('input[name=base]').forEach(x=>x.addEventListener('change',e=>{state.satellite=e.target.value==='satellite';setVisible('satellite',state.satellite);updateLegend()}));
document.querySelectorAll('input[name=popmode]').forEach(x=>x.addEventListener('change',e=>{state.popmode=e.target.value;updatePopulationMode()}));
document.getElementById('landUse').addEventListener('change',e=>{state.landUse=e.target.checked;setVisible('landuse',state.landUse);updateLegend()});
document.getElementById('settlements').addEventListener('change',e=>{state.settlements=e.target.checked;setSettlementsVisible(state.settlements);updateLegend()});
document.getElementById('rail').addEventListener('change',e=>setVisible('rail',e.target.checked));document.getElementById('roads').addEventListener('change',e=>setVisible('roads',e.target.checked));
document.getElementById('east').addEventListener('click',()=>map.flyTo({center:[150.5,-33.5],zoom:4.2}));document.querySelectorAll('[data-jump]').forEach(b=>b.addEventListener('click',()=>map.flyTo({...jumps[b.dataset.jump],duration:900})));
document.getElementById('closeDetail').addEventListener('click',()=>{document.getElementById('detailContent').innerHTML='<div class="eyebrow">MAP KEY</div><h2>Population & place</h2><p>Click an SA2, LGA or settlement marker for details.</p>';updateLegend()});