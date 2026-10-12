const {chromium}=require('playwright');
const fs=require('fs'),{spawn}=require('child_process');
(async()=>{
  const html=fs.readFileSync('escena.html','utf8').replace('__PERFIL__',fs.readFileSync('perfil.json','utf8'));
  fs.writeFileSync('build.html',html);
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1920,height:1080}});
  await p.goto('file://'+process.cwd()+'/build.html'); await p.evaluate(()=>document.fonts.ready);
  const stills=process.argv[2];
  if(stills){ for(const s of stills.split(',')){ await p.evaluate(t=>render(t),+s); await p.screenshot({path:`still_${s}.png`}); } await b.close(); return; }
  const fps=25, dur=await p.evaluate(()=>DUR), out=process.argv[3]||'video.mp4';
  const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',''+fps,'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-preset','medium','-movflags','+faststart',out],{stdio:['pipe','inherit','inherit']});
  for(let i=0;i<fps*dur;i++){ await p.evaluate(t=>render(t),i/fps); const buf=await p.screenshot({type:'jpeg',quality:93}); if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r)); }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close();
})();
