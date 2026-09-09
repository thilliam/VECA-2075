const catalogue=[
 {id:'population',group:'People',label:'Regional plan population',file:'population.geojson',kind:'point',minZoom:3,default:true},
 {id:'rail',group:'Transport',label:'Operational rail network',file:'rail.geojson',kind:'line',minZoom:4,default:true},
 {id:'roads',group:'Transport',label:'Major roads',file:'roads.geojson',kind:'line',minZoom:5,default:false},
 {id:'infrastructure',group:'Social infrastructure',label:'Health / anchor assets',file:'infrastructure.geojson',kind:'point',minZoom:5,default:true},
 {id:'education',group:'Social infrastructure',label:'Universities / TAFE',file:'education.geojson',kind:'point',minZoom:5.5,default:true}
];
const statusColours={existing:'#82d7ff',committed:'#8be28b',planned:'#ffd166'};
const map=new maplibregl.Map({container:'map',style:'https://demotiles.maplibre.org/style.json',center:[150.5,-33.5],zoom:4.2,minZoom:3,maxZoom:14});
map.addControl(new maplibregl.NavigationControl(),'bottom-right');
const enabledLayers=new Set(catalogue.filter(x=>x.default).map(x=>x.id));
const enabledStatuses=new Set(['existing','committed','planned']);
const rawData={}; let selectedYear=2050;
const jumps={seq:{center:[152.4,-27.55],zoom:7},'central-coast':{center:[151.33,-33.28],zoom:8},'new-england':{center:[151.15,-30.75],zoom:6.7},canberra:{center:[149.13,-35.28],zoom:9},riverina:{center:[147.5,-35.5],zoom:6.4},gippsland:{center:[146.5,-38],zoom:7}};

function filterData(id){const d=rawData[id]||{type:'FeatureCollection',features:[]};return {...d,features:d.features.filter(f=>enabledStatuses.has(f.properties.status||'existing')&&Number(f.properties.valid_from||2026)<=selectedYear)}}
function layerIds(id){return [`${id}-case`,id,`${id}-labels`].filter(x=>map.getLayer(x));}
function setVisibility(id,on){layerIds(id).forEach(x=>map.setLayoutProperty(x,'visibility',on?'visible':'none'));}
function refresh(){catalogue.forEach(l=>{const s=map.getSource(l.id);if(s)s.setData(filterData(l.id));});}

function buildControls(){const root=document.getElementById('layerControls');root.innerHTML='';for(const group of [...new Set(catalogue.map(x=>x.group))]){const wrap=document.createElement('div');wrap.className='layer-group';wrap.innerHTML=`<div class="layer-group-title">${group}</div>`;catalogue.filter(x=>x.group===group).forEach(layer=>{const count=rawData[layer.id]?.features?.length||0;const label=document.createElement('label');label.className='check-row';label.innerHTML=`<input type="checkbox" data-layer="${layer.id}" ${layer.default?'checked':''}/> ${layer.label}<span class="count">${count.toLocaleString()}</span>`;wrap.appendChild(label)});root.appendChild(wrap)}}

function pointRadius(id){if(id==='population')return ['interpolate',['linear'],['coalesce',['to-number',['get','future_population']],['to-number',['get','current_or_base_population']],100000],50000,7,500000,14,2000000,23,6000000,32];return ['interpolate',['linear'],['zoom'],4,4,10,8]}
function addLayer(def){const id=def.id;map.addSource(id,{type:'geojson',data:filterData(id)});if(def.kind==='line'){
 const core=id==='roads'?'#d7ba74':'#64d7ff';const width=id==='roads'?['interpolate',['linear'],['zoom'],5,1,11,3]:['interpolate',['linear'],['zoom'],4,1.6,11,4];
 map.addLayer({id:`${id}-case`,type:'line',source:id,minzoom:def.minZoom,paint:{'line-color':'#0b1217','line-width':['interpolate',['linear'],['zoom'],4,3,11,7],'line-opacity':0.7}});
 map.addLayer({id,type:'line',source:id,minzoom:def.minZoom,paint:{'line-color':core,'line-width':width,'line-opacity':id==='roads'?0.65:0.88}});
 } else {
 map.addLayer({id:`${id}-case`,type:'circle',source:id,minzoom:def.minZoom,paint:{'circle-radius':['+',pointRadius(id),2],'circle-color':'#0d141a','circle-opacity':0.75}});
 map.addLayer({id,type:'circle',source:id,minzoom:def.minZoom,paint:{'circle-radius':pointRadius(id),'circle-color':['match',['get','status'],'existing',statusColours.existing,'committed',statusColours.committed,'planned',statusColours.planned,'#fff'],'circle-stroke-color':'#0d141a','circle-stroke-width':1}});
 map.addLayer({id:`${id}-labels`,type:'symbol',source:id,minzoom:Math.max(def.minZoom+1,5),layout:{'text-field':['get','name'],'text-size':11,'text-offset':[0,1.2],'text-anchor':'top','text-allow-overlap':false},paint:{'text-color':'#f2f6f8','text-halo-color':'#111b22','text-halo-width':1.5}});
 }
 setVisibility(id,enabledLayers.has(id));wireClicks(id)}

function showDetail(feature){const p=feature.properties||{};const panel=document.getElementById('detailPanel');panel.classList.remove('empty');const source=p.source_url||p.source_dataset||p.source_note||'—';const interpretation=p.veca_interpretation||p.capital_implication||p.geometry_note||'No VECA interpretation recorded for this feature.';document.getElementById('detailContent').innerHTML=`<div class="eyebrow">${String(p.domain||'VECA').toUpperCase()}</div><h2>${p.name||'Unnamed feature'}</h2><div><span class="tag">${p.status||'existing'}</span><span class="tag">${p.geometry_quality||'source geometry'}</span></div><dl class="detail-grid"><dt>ID</dt><dd>${p.entity_id||'—'}</dd><dt>Jurisdiction</dt><dd>${p.jurisdiction||p.source_jurisdiction||'—'}</dd><dt>Source class</dt><dd>${p.source_class||p.asset_type||'—'}</dd><dt>Population</dt><dd>${p.current_or_base_population||'—'}${p.future_population?` → ${p.future_population}`:''}</dd><dt>Source</dt><dd>${source}</dd></dl><div class="section-title">VECA interpretation</div><div class="interpretation">${interpretation}</div>${p.source_url?`<a class="source-link" target="_blank" rel="noopener" href="${p.source_url}">Open source / evidence ↗</a>`:''}`}
function wireClicks(id){map.on('click',id,e=>{if(e.features?.[0])showDetail(e.features[0])});map.on('mouseenter',id,()=>map.getCanvas().style.cursor='pointer');map.on('mouseleave',id,()=>map.getCanvas().style.cursor='')}

async function loadData(){try{const [manifest,...datasets]=await Promise.all([fetch('./data/manifest.json').then(r=>{if(!r.ok)throw new Error('manifest');return r.json()}),...catalogue.map(x=>fetch(`./data/${x.file}`).then(r=>{if(!r.ok)throw new Error(x.file);return r.json()}))]);catalogue.forEach((x,i)=>rawData[x.id]=datasets[i]);buildControls();catalogue.forEach(addLayer);const total=Object.values(manifest).reduce((a,x)=>a+(x.features||0),0);document.getElementById('buildNote').textContent=`POC-002 derivatives loaded · ${total.toLocaleString()} mapped features`;}
catch(err){console.error(err);document.getElementById('buildNote').textContent='POC-002 data not built — run: python tools/build_map_poc002.py';document.getElementById('layerControls').innerHTML='<div style="color:#ffd166">Generated data missing. Run the POC-002 build command from the repo root, then refresh.</div>';}}

map.on('load',loadData);
document.getElementById('layerControls').addEventListener('change',e=>{const id=e.target.dataset.layer;if(!id)return;e.target.checked?enabledLayers.add(id):enabledLayers.delete(id);setVisibility(id,e.target.checked)});
document.querySelectorAll('[data-status]').forEach(el=>el.addEventListener('change',e=>{const s=e.target.dataset.status;e.target.checked?enabledStatuses.add(s):enabledStatuses.delete(s);refresh()}));
document.getElementById('year').addEventListener('input',e=>{selectedYear=Number(e.target.value);document.getElementById('yearLabel').textContent=selectedYear;refresh()});
document.getElementById('resetView').addEventListener('click',()=>map.flyTo({center:[150.5,-33.5],zoom:4.2}));
document.querySelectorAll('[data-jump]').forEach(el=>el.addEventListener('click',()=>map.flyTo({...jumps[el.dataset.jump],duration:900})));
document.getElementById('closeDetail').addEventListener('click',()=>document.getElementById('detailPanel').classList.add('empty'));
