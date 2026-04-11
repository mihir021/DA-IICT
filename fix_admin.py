"""
Fix admin.html:
1. Move Forecasting Lab JS back inside <script> tag
2. Replace old Electronics/Sports feed with grocery feed
3. Fix closing tags
"""

SRC = r"e:\DA IICT V.01\DA-IICT\frontend\admin.html"

with open(SRC, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Original lines: {len(lines)}")

# Keep lines 1-805 (the good part: CSS + HTML + dynamic JS)
# Line 806 is </script> — we keep it but move it to the end
# Lines 807-945 are the broken forecasting JS outside script + old feed

head = lines[:805]  # index 0-804 = lines 1-805 (ends right before </script>)

# Now build the forecasting lab JS (cleaned up, grocery-only)
forecast_js = """
/* =========== Forecasting Lab =========== */
const flabTabs=[...document.querySelectorAll('.forecast-tab-btn')];
const flabPanes=[...document.querySelectorAll('.forecast-tab-pane')];
flabTabs.forEach(btn=>btn.addEventListener('click',()=>{
  flabTabs.forEach(b=>b.classList.remove('active'));
  flabPanes.forEach(p=>p.classList.remove('active'));
  btn.classList.add('active');
  const pane=document.getElementById(`forecast-tab-${btn.dataset.forecastTab}`);
  if(pane) pane.classList.add('active');
}));

const flabCollapseBtn=document.getElementById('flabCollapseBtn');
const flabNoteBody=document.getElementById('flabNoteBody');
if(flabCollapseBtn&&flabNoteBody){
  flabCollapseBtn.addEventListener('click',()=>{
    const hidden=flabNoteBody.style.display==='none';
    flabNoteBody.style.display=hidden?'block':'none';
    flabCollapseBtn.textContent=hidden?'\\u25be Collapse':'\\u25b8 Expand';
  });
}

const srcKaggle=document.getElementById('srcKaggle');
const srcUpload=document.getElementById('srcUpload');
const kaggleNote=document.getElementById('kaggleNote');
const uploadZone=document.getElementById('uploadZone');
function setSrc(mode){
  const isK=mode==='kaggle';
  srcKaggle.classList.toggle('active',isK);
  srcUpload.classList.toggle('active',!isK);
  kaggleNote.style.display=isK?'block':'none';
  uploadZone.style.display=isK?'none':'block';
}
if(srcKaggle&&srcUpload){srcKaggle.addEventListener('click',()=>setSrc('kaggle'));srcUpload.addEventListener('click',()=>setSrc('upload'));}

const trainBtn=document.getElementById('trainModelBtn');
const trainProgress=document.getElementById('trainProgress');
const trainLog=document.getElementById('trainLog');
const trainBar=document.getElementById('trainBar');
const modelResults=document.getElementById('modelResults');
const forecastChart=document.getElementById('forecastChart');
const forecastTable=document.getElementById('forecastTable');
let trained=false;
if(trainBtn){
  trainBtn.addEventListener('click',()=>{
    if(trained) return;
    trained=true;
    trainBtn.style.display='none';
    trainProgress.classList.add('active');
    trainLog.innerHTML='';
    const lines= ['[00:00] Loading grocery sales data...','[00:01] Encoding categories and time features...','[00:03] Engineering features: lag_7, lag_14, lag_28...','[00:04] Splitting: 80% train (2013\\u20132016), 20% test (2017)...','[00:09] Evaluating on test set...','[00:10] \\u2705 Training complete!'];
    let i=0;
    trainBar.style.width='0%';
    setTimeout(()=>{trainBar.style.width='100%';},80);
    const iv=setInterval(()=>{
      if(i<lines.length){
        const d=document.createElement('div');d.className='feed-line';d.textContent=lines[i];trainLog.appendChild(d);trainLog.scrollTop=trainLog.scrollHeight;i++;
      } else {
        clearInterval(iv);
        setTimeout(()=>{
          trainProgress.classList.remove('active');
          modelResults.classList.add('active');
          forecastChart.style.display='block';
          forecastTable.style.display='block';
          showToast('Forecast model trained successfully','#66E3F2');
        },800);
      }
    },1500);
  });
}

/* Product search autocomplete */
const productSearch=document.getElementById('productSearch');
const productSuggestions=document.getElementById('productSuggestions');
if(productSearch&&productSuggestions){
  productSearch.addEventListener('focus',()=>productSuggestions.classList.add('active'));
  productSearch.addEventListener('blur',()=>setTimeout(()=>productSuggestions.classList.remove('active'),120));
  productSuggestions.querySelectorAll('.suggest-item').forEach(item=>{
    item.addEventListener('click',()=>{productSearch.value=item.textContent;productSuggestions.classList.remove('active');});
  });
}

/* Price prediction */
const predictPriceBtn=document.getElementById('predictPriceBtn');
const priceFormWrap=document.getElementById('priceFormWrap');
const predictSpinner=document.getElementById('predictSpinner');
const predictResult=document.getElementById('predictResult');
const strategySelect=document.getElementById('strategySelect');
const usedStrategy=document.getElementById('usedStrategy');
if(predictPriceBtn){
  predictPriceBtn.addEventListener('click',()=>{
    priceFormWrap.style.display='none';
    predictSpinner.classList.add('active');
    setTimeout(()=>{
      predictSpinner.classList.remove('active');
      if(usedStrategy) usedStrategy.textContent=strategySelect.value;
      predictResult.classList.add('active');
    },1500);
  });
}
const tryStrategyBtn=document.getElementById('tryStrategyBtn');
if(tryStrategyBtn){tryStrategyBtn.addEventListener('click',()=>{predictResult.classList.remove('active');priceFormWrap.style.display='block';});}
const applySingleBtn=document.getElementById('applySingleBtn');
if(applySingleBtn){applySingleBtn.addEventListener('click',()=>showToast('Applied price update for Amul Full Cream Milk','#7CB99A'));}
const applyAllBtn=document.getElementById('applyAllBtn');
if(applyAllBtn){applyAllBtn.addEventListener('click',()=>showToast('Applied all recommended price changes','#7CB99A'));}

"""

# Build output
output = []
output.extend(head)
output.append(forecast_js + "\n")
output.append("</script>\n")
output.append("</body>\n")
output.append("</html>\n")

with open(SRC, "w", encoding="utf-8") as f:
    f.writelines(output)

print(f"Fixed! New file has {sum(1 for line in open(SRC, 'r', encoding='utf-8'))} lines")
print("- Forecasting Lab JS moved inside <script> tag")
print("- Old Electronics/Sports feed removed (new grocery feed already in dynamic JS)")
print("- Proper </script></body></html> closing")
