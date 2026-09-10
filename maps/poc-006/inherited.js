// Resilient inherited-layer loader for POC-006.
// POC-004 app.js uses ./data for its own generated system layers; when reused
// from /poc-006/ those URLs resolve to the wrong directory and its Promise.all
// aborts the whole inherited-map load. POC-006 therefore loads the inherited
// datasets explicitly and independently, so one missing optional layer cannot
// suppress towns/population/roads/rail.

async function loadPoc006Inherited(){
  const specs = [
    ['sa2','../poc-003/data/population_sa2.geojson'],
    ['lga','../poc-003/data/population_lga.geojson'],
    ['settlements','../poc-003/data/settlements.geojson'],
    ['rail','../poc-002/data/rail.geojson'],
    ['roads','../poc-002/data/roads.geojson'],
    ['health','../poc-002/data/infrastructure.geojson'],
    ['education','../poc-002/data/education.geojson'],
    ['transmission','../poc-004/data/transmission_projects.geojson'],
    ['rez','../poc-004/data/energy_zones.geojson'],
    ['capital','../poc-004/data/capital_projects.geojson'],
    ['freight','../poc-004/data/freight_intermodal.geojson'],
    ['water','../poc-004/data/water_systems.geojson'],
    ['planning','../poc-004/data/planning_optionality.geojson']
  ];

  const results = await Promise.allSettled(specs.map(async ([name,url])=>[name,await j(url)]));
  const data = {};
  const failed = [];
  for(let i=0;i<results.length;i++){
    const r=results[i];
    if(r.status==='fulfilled') data[r.value[0]]=r.value[1];
    else failed.push(specs[i][0]);
  }

  // Add only if the original POC-004 loader has not already done so.
  if(!map.getSource('satellite')) addRaster();
  if(data.sa2 && data.lga && !map.getSource('population-sa2')) addPopulation(data.sa2,data.lga);
  if(data.rail && !map.getSource('rail')) addLine('rail',data.rail,'#6fd8ff',4,state.rail);
  if(data.roads && !map.getSource('roads')) addLine('roads',data.roads,'#d7ba74',5,state.roads);
  if(data.settlements && !map.getSource('settlements')) addSettlements(data.settlements);

  const pointLayers = [
    ['health','#ff6b6b',5,7,7],['education','#72e0a5',5,7,7],
    ['transmission','#ff4fbf',4,8,6],['rez','#ffd166',4,10,6],
    ['water','#39c6d6',4,9,6],['planning','#9bde5a',4,9,6],
    ['capital','#ff8c42',4,7,7],['freight','#b48cff',5,8,7]
  ];
  for(const [id,colour,minzoom,radius,labelZoom] of pointLayers){
    if(data[id] && !map.getSource(id)) addPoints(id,data[id],colour,minzoom,!!state[id],radius,labelZoom);
  }

  if(data.settlements) setSettlementsVisible(state.settlements);
  updatePopulationMode();
  updateLegend();

  const core = ['sa2','lga','settlements','rail'].filter(x=>data[x]).length;
  const note = document.getElementById('buildNote');
  if(note){
    note.textContent = failed.length
      ? `POC-006 terrain · inherited core ${core}/4 · optional missing: ${failed.join(', ')}`
      : 'POC-006 terrain · inherited VECA layers loaded';
  }
}

map.on('load',()=>{
  loadPoc006Inherited().catch(err=>{
    console.error('POC-006 inherited layer load failed',err);
    const note=document.getElementById('buildNote');
    if(note) note.textContent='POC-006 terrain loaded · inherited layers failed (see console)';
  });
});
