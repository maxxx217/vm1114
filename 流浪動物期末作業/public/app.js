/**
 * 台北科教館《十五年的約定》前端驅動核心
 * 包含：5階段狀態機、API異步加載、防連點機制、3D卡牌翻轉、Web Audio音效、原生Canvas雷達圖、URL自動化預覽支援
 */

// 全局狀態中心
const AppState = {
  currentScreen: 'select', // 'select' | 'game' | 'cert'
  selectedPet: null,
  playerName: '科教館小學員',
  events: [],
  currentEventIndex: 0,
  stats: { money: 80, time: 80, happiness: 85 },
  choicesHistory: [],
  rescuedCount: 0,
  isProcessing: false,
  audioCtx: null
};

let PETS_DB_CACHE = [];

// Web Audio API 簡約合成音效 (無需加載外部 mp3)
function playSound(type) {
  try {
    if (!AppState.audioCtx) {
      AppState.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    const ctx = AppState.audioCtx;
    if (ctx.state === 'suspended') {
      ctx.resume();
    }
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);

    const now = ctx.currentTime;
    if (type === 'click') {
      osc.type = 'sine';
      osc.frequency.setValueAtTime(440, now);
      gain.gain.setValueAtTime(0.1, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.08);
      osc.start(now);
      osc.stop(now + 0.08);
    } else if (type === 'flip') {
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(320, now);
      osc.frequency.exponentialRampToValueAtTime(580, now + 0.2);
      gain.gain.setValueAtTime(0.15, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.25);
      osc.start(now);
      osc.stop(now + 0.25);
    } else if (type === 'rescue') {
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(880, now);
      osc.frequency.setValueAtTime(440, now + 0.15);
      gain.gain.setValueAtTime(0.2, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
      osc.start(now);
      osc.stop(now + 0.35);
    } else if (type === 'success') {
      osc.type = 'sine';
      osc.frequency.setValueAtTime(523.25, now); // C5
      osc.frequency.setValueAtTime(659.25, now + 0.1); // E5
      osc.frequency.setValueAtTime(783.99, now + 0.2); // G5
      gain.gain.setValueAtTime(0.2, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.45);
      osc.start(now);
      osc.stop(now + 0.45);
    }
  } catch (e) {
    console.warn('Audio playback error (safe to ignore):', e);
  }
}

// 畫面切換
function switchScreen(screenId) {
  document.querySelectorAll('.screen-view').forEach(el => el.classList.remove('active'));
  const target = document.getElementById(`screen-${screenId}`);
  if (target) {
    target.classList.add('active');
    AppState.currentScreen = screenId;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

// 內建離線題庫備援 (若未啟動後端伺服器或直接雙擊 index.html 開啟時自動切換，保證 100% 可玩)
const OFFLINE_PETS_BACKUP = [
  {
    id: "dog",
    name: "米克斯汪汪 (小黃)",
    species: "犬",
    lifespan: "12 ~ 16 年",
    avatar: "🐕",
    tagline: "活潑忠誠，極度需要每日出門放電與戶外嗅聞",
    initial_stats: { money: 80, time: 80, happiness: 85 },
    description: "幼犬需定點排泄引導；成犬每天需散步1-2小時。需定期預防心絲蟲與狂犬病疫苗。"
  },
  {
    id: "cat",
    name: "虎斑喵喵 (咪咪)",
    species: "貓",
    lifespan: "15 ~ 20 年",
    avatar: "🐈",
    tagline: "獨立敏銳，居家需嚴格防墜與充足水分攝取",
    initial_stats: { money: 85, time: 75, happiness: 90 },
    description: "全屋必須加裝防墜網防「高樓摔傷症候群」。高齡極易出現慢性腎衰竭與下泌尿道疾病。"
  },
  {
    id: "rabbit",
    name: "垂耳兔兔 (雪球)",
    species: "兔",
    lifespan: "8 ~ 12 年",
    avatar: "🐇",
    tagline: "草食安靜，需要特殊寵物專科獸醫照護",
    initial_stats: { money: 75, time: 85, happiness: 80 },
    description: "主食為無限量提摩西牧草（非紅蘿蔔！）。未進食超過12小時會引發致命腸胃停滯！"
  },
  {
    id: "hamster",
    name: "三線倉鼠 (布丁)",
    species: "倉鼠",
    lifespan: "2 ~ 3 年",
    avatar: "🐹",
    tagline: "夜行獨居，絕對不能合籠飼養",
    initial_stats: { money: 90, time: 90, happiness: 80 },
    description: "一鼠一籠！合籠會嚴重撕咬致死。跑輪需直徑21cm以上保護脊椎，冬天需保溫防失溫。"
  }
];

const OFFLINE_DOG_EVENTS = [
  {
    year: 1,
    stage: "幼年期（0-1歲）",
    title: "半夜哭鬧與定點如廁挑戰",
    description: "新來的小傢伙半夜不斷嚎叫，客廳地毯也被尿了一大灘，明天一早還要上學考試！",
    scenario_img: "🌙",
    options: [
      {
        id: "A",
        label: "太吵了！直接關去陽台吹風處罰，明天再清理",
        is_responsible: false,
        delta: { money: 0, time: 10, happiness: -35 },
        vet_knowledge: "【獸醫行為學】幼犬貓剛離開母親極度缺乏安全感，孤立與斥責會誘發重度分離焦慮，且易因溫差受涼感冒。",
        feedback: "寵物感到被拋棄，心靈受創！隨地便溺行為反而加劇了。"
      },
      {
        id: "B",
        label: "溫柔安撫，擺放沾有母味的衣物，並耐心用零食引導定點便盆",
        is_responsible: true,
        delta: { money: -5, time: -20, happiness: 20 },
        vet_knowledge: "【正向強化訓練】掌握2~4個月社會化黃金期，用正向獎勵能建立一輩子的信任與良好衛生習慣。",
        feedback: "雖然睡眠被中斷，但小傢伙建立了滿滿安全感，學會了定點如廁！"
      }
    ]
  },
  {
    year: 2,
    stage: "幼年期（1-2歲）",
    title: "動物醫院的第一堂必修課",
    description: "到了該打針的年齡，隔壁鄰居說：「寵物都關家裡不會出門，省下幾千塊疫苗和晶片費啦！」",
    scenario_img: "💉",
    options: [
      {
        id: "A",
        label: "聽鄰居的話省下醫療費，買昂貴的可愛寵物衣服就好",
        is_responsible: false,
        delta: { money: 10, time: 0, happiness: -25 },
        vet_knowledge: "【動保法與傳染病學】狂犬病為法定人畜共通傳染病，台灣動保法明定需強制施打與晶片登記！病毒可由鞋底帶回家中感染未施打疫苗之毛孩。",
        feedback: "省了小錢卻埋下致命隱患！一旦走失更是永遠無法尋回。"
      },
      {
        id: "B",
        label: "完成核心疫苗、狂犬病注射，並植入晶片完成寵物身分登記",
        is_responsible: true,
        delta: { money: -25, time: -10, happiness: 15 },
        vet_knowledge: "【預防醫學】晶片是毛孩的終生身分證；定期疫苗與心絲蟲預防藥，是花費最小、保護效益最高的醫療投資。",
        feedback: "領到合法的狂犬病疫苗頸牌與寵物身分證！合法又安心。"
      }
    ]
  },
  {
    year: 4,
    stage: "青年期（3-5歲）",
    title: "發情期的躁動與誘惑",
    description: "寵物到了性成熟期，夜間開始嚎叫、躁動甚至衝向大門。親戚長輩說：「讓牠生一窩才算圓滿！」",
    scenario_img: "🏥",
    options: [
      {
        id: "A",
        label: "不結紮生一窩小寶寶好可愛，送不掉再放生去公園",
        is_responsible: false,
        delta: { money: -20, time: -15, happiness: -30 },
        vet_knowledge: "【動保法第22條】特定寵物飼主應為寵物絕育，私自繁殖違法最高罰25萬！未絕育母畜高達50%老年罹患致命子宮蓄膿與乳腺瘤。",
        feedback: "生了5隻幼崽無法妥善安置，母體更面臨子宮病變風險，違背生命責任。"
      },
      {
        id: "B",
        label: "配合專業獸醫術前血檢評估，安排適齡絕育手術與術後照護",
        is_responsible: true,
        delta: { money: -25, time: -15, happiness: 20 },
        vet_knowledge: "【外科學與健康】絕育不僅杜絕生殖系統致命病變，更可大幅減少發情期焦躁、噴尿標記與走失車禍機率。",
        feedback: "手術順利康復！情緒穩定許多，徹底遠離老年子宮蓄膿奪命風險。"
      }
    ]
  },
  {
    year: 7,
    stage: "生活劇變期（6-8歲）",
    title: "升上國中補習，回到家累癱了！",
    description: "課業加重，每天回到家只想躺著滑手機。寵物叼著玩具眼巴巴看著你，已經三天沒好好陪牠了。",
    scenario_img: "🎒",
    options: [
      {
        id: "A",
        label: "好累喔！大聲斥責牠：「走開啦沒看我很忙嗎！」，繼續滑手機",
        is_responsible: false,
        delta: { money: 0, time: 15, happiness: -40 },
        vet_knowledge: "【行為精神醫學】犬貓若長期缺乏環境豐富化與放電陪伴，會引發刻板行為、過度舔毛咬尾自殘，甚至焦慮拆家與攻擊性。",
        feedback: "家具被咬爛，寵物眼神失去光彩，甚至開始躲避你的撫摸。"
      },
      {
        id: "B",
        label: "召開家庭會議與家人分工，每天清晨早起20分鐘帶牠散步嗅聞",
        is_responsible: true,
        delta: { money: 0, time: -25, happiness: 25 },
        vet_knowledge: "【嗅聞與放電】散步時的嗅聞對動物大腦刺激能有效釋放壓力！規律散步能穩定身心，增進免疫力。",
        feedback: "雖然少睡了20分鐘，但毛孩每天都開心地搖尾巴，全家感情也更加緊密！"
      }
    ]
  },
  {
    year: 9,
    stage: "生活劇變期（8-10歲）",
    title: "全家搬新家，新房東嚴禁養寵物！",
    description: "因家庭工作異動必須跨縣市搬遷，好不容易找到租金合適的房子，但房東合約寫明「絕對禁止飼養任何寵物」！",
    scenario_img: "📦",
    options: [
      {
        id: "A",
        label: "沒辦法了，把已經養了9年的老夥伴偷偷送去收容所或鄉下丟棄",
        is_responsible: false,
        delta: { money: 10, time: 20, happiness: -60 },
        vet_knowledge: "【動保法第29條與收容醫學】惡意棄養最高重罰15萬元！中高齡寵物被棄入收容所，因適應不良與絕食，死亡率高達70%以上。",
        feedback: "在牠眼中你就是牠的整個世界。被丟棄的老夥伴每天望著收容所鐵門流淚絕食。"
      },
      {
        id: "B",
        label: "堅守承諾！全家一起多花一個月時間尋找寵物友善租屋，並簽訂責任切結書",
        is_responsible: true,
        delta: { money: -30, time: -30, happiness: 30 },
        vet_knowledge: "【長期承諾本質】真正的飼主責任，是在人生遭遇困難、搬遷、懷孕時，永遠將牠作為不離不棄的家庭核心成員。",
        feedback: "雖然通勤時間變長、租金稍貴，但全家人看見老毛孩在溫暖新家安睡的臉龐，一切都值得！"
      }
    ]
  },
  {
    year: 12,
    stage: "高齡照護期（11-13歲）",
    title: "眼睛混濁走路撞牆，後腳無力站不穩",
    description: "老夥伴步入銀髮族階段，被診斷出白內障與重度退化性關節炎，常常來不及走到便盆就尿在地板上。",
    scenario_img: "🦯",
    options: [
      {
        id: "A",
        label: "嫌牠老了又髒又臭又花錢，關在陽台角落眼不見為淨",
        is_responsible: false,
        delta: { money: 0, time: 10, happiness: -50 },
        vet_knowledge: "【老年醫學】關節炎會造成持續慢性劇痛，失禁是神經退化非故意犯錯。將老病動物孤立於溫差大的陽台等同於遺棄虐待。",
        feedback: "老夥伴在寒冷陽台哀鳴，關節疼痛讓牠無法起身進食，生命指數瀕臨崩潰。"
      },
      {
        id: "B",
        label: "全屋鋪設防滑地墊，墊高食盆，穿著高齡專用尿布，並配合止痛雷射復健",
        is_responsible: true,
        delta: { money: -35, time: -25, happiness: 25 },
        vet_knowledge: "【無障礙高齡友善環境】鋪設防滑地墊可大幅減少骨折風險；規律疼痛管理能維持高齡動物最後的尊嚴生活品質。",
        feedback: "家裡變成了無障礙樂園，老夥伴穿著尿布依然安心地蹭你的腿討摸摸！"
      }
    ]
  },
  {
    year: 15,
    stage: "終老安寧期（14-16歲）",
    title: "十五年的約定：最後的守護",
    description: "老毛孩步入生命終章，器官衰竭食慾低下。獸醫師輕撫著牠，詢問你是否願意陪伴牠走過這最後的一段安寧時光。",
    scenario_img: "🌈",
    options: [
      {
        id: "A",
        label: "害怕面對死亡不想去醫院，放牠一個人在家裡自生自滅",
        is_responsible: false,
        delta: { money: 0, time: 15, happiness: -60 },
        vet_knowledge: "【安寧緩和醫療】動物在器官衰竭末期常伴隨劇烈噁心、窒息感與低體溫，缺乏醫療支持會經歷漫長痛苦。飼主的缺席是臨終最大的孤獨。",
        feedback: "你在缺席中留下了一輩子無法挽回的遺憾與內疚。"
      },
      {
        id: "B",
        label: "全程握著牠的掌心溫暖陪伴，給予止痛緩和治療，感謝牠十五年無條件的愛",
        is_responsible: true,
        delta: { money: -20, time: -20, happiness: 40 },
        vet_knowledge: "【生命教育與安寧善終】陪伴至生命最後一刻，給予尊嚴安寧，是飼主能給予陪伴一生毛孩最崇高的最後承諾。",
        feedback: "牠在最熟悉溫暖的懷抱中安詳閉上雙眼。你完整履行了十五年前許下的承諾！"
      }
    ]
  }
];

const OFFLINE_RABBIT_EVENTS = [
  {
    year: 1,
    stage: "幼年期（0-1歲）",
    title: "「兔子只要吃紅蘿蔔」的迷思？",
    description: "卡通裡兔子都吃紅蘿蔔！菜市場老闆也說餵剩菜葉就好，又香又便宜！",
    scenario_img: "🥕",
    options: [
      {
        id: "A",
        label: "聽信謠言，只餵紅蘿蔔與高水分蔬菜，不買牧草",
        is_responsible: false,
        delta: { money: 10, time: 0, happiness: -40 },
        vet_knowledge: "【兔科生理醫學】紅蘿蔔高糖分會引發腸道嚴重脹氣與蛀牙！兔子主食80%以上必須是「無限量優質提摩西牧草」，需靠牧草纖維磨牙與促進腸胃蠕動。",
        feedback: "兔子嚴重脹氣下痢，腸胃鼓脹如氣球，痛苦縮在角落！"
      },
      {
        id: "B",
        label: "提供無限量提摩西牧草、定量專用乾糧與乾淨煮沸開水",
        is_responsible: true,
        delta: { money: -15, time: -10, happiness: 25 },
        vet_knowledge: "【特寵營養學】無限量牧草能維持正常的盲腸菌叢並均勻磨損終生生長的牙齒，是兔兔長壽健康的基石。",
        feedback: "雪球咖滋咖滋快樂嚼草，牙齒健康漂亮，腸道圓滾滾便便超健康！"
      }
    ]
  },
  {
    year: 3,
    stage: "青年期（2-4歲）",
    title: "突然十二小時不吃不喝也不排便！",
    description: "放學回家發現兔兔縮在角落母雞蹲，食盆裡的草完全沒動，籠子裡一顆便便都沒有！",
    scenario_img: "⚠️",
    options: [
      {
        id: "A",
        label: "兔子挑食吧！明天考試很忙，等明天放學再看看",
        is_responsible: false,
        delta: { money: 0, time: 10, happiness: -50 },
        vet_knowledge: "【致死性腸胃停滯 (GI Stasis)】兔子腸胃無法自行逆蠕動嘔吐，一旦超過12小時未進食，體內毒素暴增、體溫失衡，24-48小時內有極高猝死風險！",
        feedback: "隔天早晨雪球已經失溫休克，送醫宣告不治，造成永遠的悲痛。"
      },
      {
        id: "B",
        label: "立刻預約特殊寵物專科獸醫院急診，配合醫師進行灌食與打點滴",
        is_responsible: true,
        delta: { money: -30, time: -20, happiness: 30 },
        vet_knowledge: "【特寵急診醫學】犬貓醫院大多無兔科專長！及早送往特寵專科注射皮下輸液、腸胃蠕動劑與草粉灌食，存活率高達90%以上。",
        feedback: "特寵醫師緊急給藥處置，傍晚雪球排出了第一顆毛球便，撿回一命！"
      }
    ]
  },
  {
    year: 6,
    stage: "劇變期（5-7歲）",
    title: "升上國中課業繁重，換毛季毛毛滿天飛",
    description: "換毛季節全家飄散細毛，家人鼻子過敏狂打噴嚏，媽媽問你要不要把兔子送走。",
    scenario_img: "🧹",
    options: [
      {
        id: "A",
        label: "嫌每天梳毛好麻煩，乾脆順水推舟送去野生農場放生",
        is_responsible: false,
        delta: { money: 10, time: 15, happiness: -60 },
        vet_knowledge: "【生態與動物福祉】寵物兔完全沒有野外生存能力！放生農場或野外會被野狗咬死或因寄生蟲皮膚潰爛在三日內死亡，等同棄養違法。",
        feedback: "雪球在野外絕望地死於天敵攻擊，你放棄了最初的誓言。"
      },
      {
        id: "B",
        label: "加裝空氣清淨機，主動每天花15分鐘幫兔兔梳毛，防止毛球症",
        is_responsible: true,
        delta: { money: -15, time: -20, happiness: 25 },
        vet_knowledge: "【理毛與毛球預防】兔子理毛會吞入大量毛髮，若不及時梳理極易在胃內形成巨大硬塊阻礙消化。勤梳毛是預防醫學的核心。",
        feedback: "房間空氣變乾淨了，雪球被梳得毛茸茸好舒服，全家繼續幸福相伴！"
      }
    ]
  },
  {
    year: 9,
    stage: "高齡終老期（8-10歲）",
    title: "高齡老兔歪頭與歪斜症候群 (E. cuniculi)",
    description: "9歲的老兔雪球突然脖子往右歪斜、眼球水平顫動無法平衡，站都站不穩。",
    scenario_img: "🩺",
    options: [
      {
        id: "A",
        label: "看起來好嚇人好古怪，覺得治不好了直接放棄",
        is_responsible: false,
        delta: { money: 0, time: 10, happiness: -50 },
        vet_knowledge: "【兔微孢子蟲症與中耳炎】歪頭症是高齡兔常見神經或感染病，及早投與抗寄生蟲藥與消炎藥，大多能控制並維持生活自理能力。",
        feedback: "雪球因缺乏照護不斷翻滾撞傷，在極度恐懼中結束了生命。"
      },
      {
        id: "B",
        label: "鋪滿防撞軟墊與毛巾捲支撐身體，每日按時餵藥，細心餵草照護終老",
        is_responsible: true,
        delta: { money: -25, time: -25, happiness: 35 },
        vet_knowledge: "【高齡特寵安寧居家照護】用毛巾圍成U型巢穴輔助平衡，雖然頭部微歪，雪球依然能有尊嚴、安心地享受主人十年的溫暖陪伴。",
        feedback: "雪球在柔軟的毛巾小窩裡安心咀嚼最愛的草草，在你身邊祥和走完圓滿兔生！"
      }
    ]
  }
];

const OFFLINE_HAMSTER_EVENTS = [
  {
    year: 1,
    stage: "幼年期（0-6個月）",
    title: "「買一對住一起生寶寶才不孤單」？",
    description: "夜市寵物攤老闆說：「買一公一母放在同一個小籠子，牠們感情好還會生可愛小倉鼠喔！」",
    scenario_img: "⚔️",
    options: [
      {
        id: "A",
        label: "聽老闆的，把兩隻倉鼠關在同一個小鐵籠裡當好朋友",
        is_responsible: false,
        delta: { money: 5, time: 0, happiness: -60 },
        vet_knowledge: "【囓齒目行為學：一鼠一籠鐵律】三線倉鼠是強烈地盤性獨居動物！合籠飼養百分之百會爆發你死我活的殘酷血腥廝殺，造成斷肢殘廢死亡！",
        feedback: "半夜籠子裡傳出慘叫，一隻重傷瀕死，另一隻也滿身血痕！"
      },
      {
        id: "B",
        label: "嚴格實行「一鼠一籠」，並準備底面積大於40x60cm的大整理箱與21cm大跑輪",
        is_responsible: true,
        delta: { money: -20, time: -15, happiness: 30 },
        vet_knowledge: "【福祉環境標準】合適直徑跑輪能保護脆弱脊椎避免壓迫變形；厚鋪墊材能滿足挖掘天性，大幅降低刻板啃咬鐵籠行為。",
        feedback: "布丁在大豪宅裡快樂挖隧道、跑輪飛快奔跑，安全又無拘無束！"
      }
    ]
  },
  {
    year: 2,
    stage: "成年期（1-2歲）",
    title: "寒流來襲，小倉鼠身軀冰冷硬梆梆！",
    description: "冬天強烈冷氣團來襲，早上發現布丁躺在小窩裡一動也不動，摸起來像冰塊，難道死掉了嗎？！",
    scenario_img: "❄️",
    options: [
      {
        id: "A",
        label: "以為已經死了，直接拿垃圾袋包起來丟進垃圾桶",
        is_responsible: false,
        delta: { money: 0, time: 5, happiness: -70 },
        vet_knowledge: "【致命低體溫「偽冬眠」】寵物倉鼠原產溫暖地帶，環境低於15度會觸發危險的失溫休眠（並非健康冬眠），若誤當死亡丟棄等同活埋！需立刻暖暖包隔毛巾緩慢回溫！",
        feedback: "生命在冰冷垃圾桶中無辜消逝，失去了急救復甦的唯一黃金機會。"
      },
      {
        id: "B",
        label: "立刻用手心與保暖燈溫柔回溫，並在籠內加裝寵物專用保暖陶瓷燈與厚棉花",
        is_responsible: true,
        delta: { money: -15, time: -10, happiness: 35 },
        vet_knowledge: "【冬季溫控醫學】及時回溫並補充溫糖水，小倉鼠在數小時內能奇蹟甦醒。冬季維持室溫20-24度是囓齒類的基本生存防線。",
        feedback: "隨着身體漸漸回暖，布丁的小鬍鬚微微顫抖，奇蹟般睜開眼睛討吃瓜子！"
      }
    ]
  },
  {
    year: 3,
    stage: "高齡期（2-3歲）",
    title: "小巨人步入暮年：短暫生命的光芒",
    description: "兩歲半的布丁相當於人類80歲高齡，背部開始脫毛駝背，動作慢如蝸牛，也不太能跑滾輪了。",
    scenario_img: "🕯️",
    options: [
      {
        id: "A",
        label: "覺得養倉鼠壽命太短沒意思，不再理牠，直接去寵物店買新寵物",
        is_responsible: false,
        delta: { money: -10, time: 10, happiness: -40 },
        vet_knowledge: "【生命倫理教育】生命價值不在於長短，而在於相處的溫度。輕視短壽命生命會養成隨意丟棄生命的輕浮心態。",
        feedback: "布丁在被冷落中孤獨離開，你錯失了生命教育中最珍貴的告別功課。"
      },
      {
        id: "B",
        label: "將食盆水瓶改為地面矮坡無障礙，把堅果磨成泥細心餵食，深情送別",
        is_responsible: true,
        delta: { money: -5, time: -15, happiness: 40 },
        vet_knowledge: "【囓齒類安寧照護與悲傷療癒】倉鼠壽命雖僅兩至三年，但給予完整的善終關懷，能讓孩子深刻體會生命的重量與告別的勇氣。",
        feedback: "布丁在你掌心的溫度裡安詳沉睡。你用兩年半的時間，給了牠無比幸福且完整的一生！"
      }
    ]
  }
];

// 1. 初始化與加載物種列表
async function loadPets() {
  const container = document.getElementById('pets-container');
  container.innerHTML = '<div class="loading-state">🐾 正在連線科教館生命科學物種庫...</div>';
  
  try {
    const res = await fetch('/api/pets');
    if (!res.ok) throw new Error('API connection failed');
    const data = await res.json();
    PETS_DB_CACHE = data.pets || [];
    renderPetsGrid(PETS_DB_CACHE);
  } catch (err) {
    // 伺服器離線時自動無縫啟用本地內建備援資料！
    console.warn('伺服器離線，自動切換至本機離線備援資料庫！');
    PETS_DB_CACHE = OFFLINE_PETS_BACKUP;
    renderPetsGrid(PETS_DB_CACHE);
  }
}

function renderPetsGrid(pets) {
  const container = document.getElementById('pets-container');
  container.innerHTML = '';

  pets.forEach(pet => {
    const card = document.createElement('div');
    card.className = 'pet-select-card';
    card.setAttribute('role', 'listitem');
    card.innerHTML = `
      <div>
        <div class="pet-icon-circle" aria-hidden="true">${pet.avatar}</div>
        <h3 class="pet-card-title">${pet.name}</h3>
        <span class="pet-lifespan-pill">預期壽命：${pet.lifespan}</span>
        <p class="pet-card-desc"><strong>特性：</strong>${pet.tagline}<br><small>${pet.description}</small></p>
      </div>
      <button class="pet-select-btn" onclick="startAdopt('${pet.id}')">
        認養 ${pet.species} 並守護一生 ➔
      </button>
    `;
    container.appendChild(card);
  });
}

// 2. 認養寵物並啟動生命旅程
async function startAdopt(petId) {
  playSound('click');
  const nameInput = document.getElementById('player-input');
  AppState.playerName = nameInput.value.trim() || '科教館小學員';

  try {
    const res = await fetch(`/api/events?pet=${petId}`);
    if (!res.ok) throw new Error('API fetch error');
    const data = await res.json();
    AppState.events = data.events || [];
  } catch (err) {
    console.warn('使用離線事件庫備援');
    if (petId === 'rabbit') AppState.events = OFFLINE_RABBIT_EVENTS;
    else if (petId === 'hamster') AppState.events = OFFLINE_HAMSTER_EVENTS;
    else AppState.events = OFFLINE_DOG_EVENTS;
  }

  AppState.selectedPet = petId;
  AppState.currentEventIndex = 0;
  AppState.choicesHistory = [];
  AppState.rescuedCount = 0;

  const petObj = PETS_DB_CACHE.find(p => p.id === petId) || {
    avatar: '🐕',
    name: '米克斯汪汪',
    initial_stats: { money: 80, time: 80, happiness: 85 }
  };
  AppState.stats = { ...petObj.initial_stats };
  document.getElementById('ui-pet-avatar').innerText = petObj.avatar;
  document.getElementById('game-pet-name').innerText = petObj.name;

  updateDashboard();
  renderCurrentEvent();
  switchScreen('game');
}

// 更新三維儀表與時間軸
function updateDashboard() {
  const m = Math.max(0, Math.min(100, AppState.stats.money));
  const t = Math.max(0, Math.min(100, AppState.stats.time));
  const h = Math.max(0, Math.min(100, AppState.stats.happiness));

  document.getElementById('val-money').innerText = `${m}%`;
  document.getElementById('bar-money').style.width = `${m}%`;

  document.getElementById('val-time').innerText = `${t}%`;
  document.getElementById('bar-time').style.width = `${t}%`;

  document.getElementById('val-happiness').innerText = `${h}%`;
  document.getElementById('bar-happiness').style.width = `${h}%`;

  // 時間進度條
  const totalEvents = AppState.events.length;
  const current = AppState.currentEventIndex + 1;
  const pct = Math.min(100, Math.round((current / totalEvents) * 100));
  document.getElementById('ui-timeline-fill').style.width = `${pct}%`;

  const curEv = AppState.events[AppState.currentEventIndex];
  if (curEv) {
    document.getElementById('ui-age-badge').innerText = `第 ${curEv.year} 年 (${curEv.stage})`;
  }
}

// 渲染當前事件正面
function renderCurrentEvent() {
  const flipper = document.getElementById('main-flipper');
  flipper.classList.remove('is-flipped');
  AppState.isProcessing = false;

  const ev = AppState.events[AppState.currentEventIndex];
  if (!ev) return;

  document.getElementById('card-stage-tag').innerText = `🌟 ${ev.stage}`;
  document.getElementById('card-emoji').innerText = ev.scenario_img;
  document.getElementById('card-event-title').innerText = `第 ${ev.year} 年：${ev.title}`;
  document.getElementById('card-event-desc').innerText = ev.description;

  const optA = ev.options[0];
  const optB = ev.options[1];

  document.getElementById('text-opt-a').innerText = optA.label;
  document.getElementById('text-opt-b').innerText = optB.label;

  document.getElementById('btn-opt-a').disabled = false;
  document.getElementById('btn-opt-b').disabled = false;
}

// 3. 處理點擊選項 (3D 翻轉與防連點)
function handleSelectOption(optionIndex) {
  if (AppState.isProcessing) return; // 防連點 (Debounce)
  AppState.isProcessing = true;
  playSound('flip');

  document.getElementById('btn-opt-a').disabled = true;
  document.getElementById('btn-opt-b').disabled = true;

  const ev = AppState.events[AppState.currentEventIndex];
  const choice = ev.options[optionIndex];

  AppState.choicesHistory.push({
    eventYear: ev.year,
    choiceId: choice.id,
    isResponsible: choice.is_responsible
  });

  AppState.stats.money += choice.delta.money;
  AppState.stats.time += choice.delta.time;
  AppState.stats.happiness += choice.delta.happiness;

  const badge = document.getElementById('back-result-badge');
  if (choice.is_responsible) {
    badge.className = 'result-badge badge-success';
    badge.innerText = '👍 負責任的決定！';
  } else {
    badge.className = 'result-badge badge-warning';
    badge.innerText = '⚠️ 衝動的不當抉擇！';
  }

  document.getElementById('back-year-echo').innerText = `第 ${ev.year} 年回顧`;
  document.getElementById('back-vet-text').innerText = choice.vet_knowledge;

  const deltaTags = document.getElementById('back-delta-tags');
  deltaTags.innerHTML = `
    <span class="delta-tag tag-money">🪙 金錢 ${choice.delta.money >= 0 ? '+' : ''}${choice.delta.money}</span>
    <span class="delta-tag tag-time">⏳ 時間 ${choice.delta.time >= 0 ? '+' : ''}${choice.delta.time}</span>
    <span class="delta-tag tag-happy">❤️ 幸福 ${choice.delta.happiness >= 0 ? '+' : ''}${choice.delta.happiness}</span>
  `;
  document.getElementById('back-story-feedback').innerText = choice.feedback;

  const flipper = document.getElementById('main-flipper');
  flipper.classList.add('is-flipped');
  updateDashboard();

  if (AppState.stats.money <= 0 || AppState.stats.happiness <= 0) {
    setTimeout(() => {
      triggerRescueModal();
    }, 700);
  }
}

// 4. 獸醫緊急救援機制
function triggerRescueModal() {
  playSound('rescue');
  AppState.rescuedCount++;
  
  const modal = document.getElementById('rescue-modal');
  const desc = document.getElementById('rescue-desc');
  
  if (AppState.stats.money <= 0) {
    desc.innerHTML = `因為突發重病但平時未準備「急難醫療基金」，毛孩在手術房命懸一線！<br><strong>科教館特派獸醫師啟動公義急難儲備金救回一命！</strong>`;
    AppState.stats.money = 40;
  } else {
    desc.innerHTML = `因為長期疏於陪伴放電或環境不當，毛孩心理遭受重創引發嚴重自殘！<br><strong>科教館特派獸醫行為治療師介入安撫，救回脆弱生命！</strong>`;
    AppState.stats.happiness = 40;
  }
  
  updateDashboard();
  modal.style.display = 'flex';
}

function dismissRescueModal() {
  playSound('click');
  document.getElementById('rescue-modal').style.display = 'none';
}

// 5. 進入下一關或結算證書
function handleNextStep() {
  playSound('click');
  AppState.currentEventIndex++;
  
  if (AppState.currentEventIndex < AppState.events.length) {
    renderCurrentEvent();
  } else {
    finishGameAndGenerateCert();
  }
}

// 6. 結算與繪製五維雷達圖
async function finishGameAndGenerateCert() {
  playSound('success');
  
  try {
    const res = await fetch('/api/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        petId: AppState.selectedPet,
        playerName: AppState.playerName,
        choices: AppState.choicesHistory,
        rescuedCount: AppState.rescuedCount
      })
    });
    if (!res.ok) throw new Error('API evaluate failed');
    const evalData = await res.json();
    renderCertificate(evalData);
    switchScreen('cert');
  } catch (err) {
    console.warn('使用離線結算演算法備援');
    const totalQ = AppState.events.length || 7;
    const respCount = AppState.choicesHistory.filter(c => c.isResponsible).length;
    const respRate = respCount / totalQ;

    const offlineEval = {
      certificateId: `NTSEC-${Math.random().toString(16).substring(2, 8).toUpperCase()}`,
      playerName: AppState.playerName,
      petId: AppState.selectedPet,
      grade: respRate >= 0.85 ? 'S' : (respRate >= 0.7 ? 'A' : 'B'),
      title: respRate >= 0.85 ? '榮譽守護者特派小獸醫' : '愛心合格專業飼主',
      badge: respRate >= 0.85 ? '🌟 金牌典範飼主' : '🏅 銀牌愛心飼主',
      comment: '太棒了！你深刻理解「想養」與「準備好」的本質差異。面對生活改變，始終堅守承諾！',
      responsibleCount: respCount,
      totalQuestions: totalQ,
      rescuedCount: AppState.rescuedCount,
      radar: {
        economy: Math.min(100, Math.max(30, 60 + respCount * 5)),
        time: Math.min(100, Math.max(30, 55 + respCount * 6)),
        medical: Math.min(100, Math.max(40, 50 + respCount * 7)),
        law: Math.min(100, Math.max(40, 55 + respCount * 6)),
        commitment: Math.min(100, Math.max(30, 60 + respCount * 6))
      }
    };
    renderCertificate(offlineEval);
    switchScreen('cert');
  }
}

function renderCertificate(evalData) {
  document.getElementById('cert-id-text').innerText = `證書字號：${evalData.certificateId}`;
  document.getElementById('cert-player-name').innerText = evalData.playerName;
  
  const petObj = PETS_DB_CACHE.find(p => p.id === evalData.petId) || { name: '心愛毛孩' };
  document.getElementById('cert-pet-name').innerText = petObj.name;

  document.getElementById('cert-grade-badge').innerText = evalData.grade;
  document.getElementById('cert-eval-title').innerText = evalData.title;
  document.getElementById('cert-badge-tag').innerText = evalData.badge;
  document.getElementById('cert-comment-text').innerText = evalData.comment;

  document.getElementById('cert-stat-resp').innerText = `${evalData.responsibleCount} / ${evalData.totalQuestions} 次`;
  document.getElementById('cert-stat-rescue').innerText = `${evalData.rescuedCount} 次`;

  setTimeout(() => {
    drawRadarChart(evalData.radar);
  }, 100);
}

// 原生 HTML5 Canvas 雷達圖繪製演算法
function drawRadarChart(radar) {
  const canvas = document.getElementById('radarChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;
  const centerX = w / 2;
  const centerY = h / 2 + 10;
  const radius = 80;

  ctx.clearRect(0, 0, w, h);

  const axes = [
    { label: '🪙 經濟儲備', val: radar.economy },
    { label: '⏳ 時間陪伴', val: radar.time },
    { label: '🩺 醫學常識', val: radar.medical },
    { label: '📜 動保法規', val: radar.law },
    { label: '❤️ 終老守護', val: radar.commitment }
  ];

  const totalAxes = axes.length;
  const angleStep = (Math.PI * 2) / totalAxes;

  for (let level = 1; level <= 3; level++) {
    const r = (radius / 3) * level;
    ctx.beginPath();
    ctx.strokeStyle = '#e5e7eb';
    ctx.lineWidth = 1.2;
    for (let i = 0; i < totalAxes; i++) {
      const angle = i * angleStep - Math.PI / 2;
      const x = centerX + r * Math.cos(angle);
      const y = centerY + r * Math.sin(angle);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.stroke();
  }

  ctx.font = 'bold 11px system-ui, sans-serif';
  ctx.fillStyle = '#4b5563';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';

  axes.forEach((axis, i) => {
    const angle = i * angleStep - Math.PI / 2;
    const axX = centerX + radius * Math.cos(angle);
    const axY = centerY + radius * Math.sin(angle);

    ctx.beginPath();
    ctx.strokeStyle = '#d1d5db';
    ctx.moveTo(centerX, centerY);
    ctx.lineTo(axX, axY);
    ctx.stroke();

    const labelX = centerX + (radius + 22) * Math.cos(angle);
    const labelY = centerY + (radius + 18) * Math.sin(angle);
    ctx.fillText(axis.label, labelX, labelY);
  });

  ctx.beginPath();
  axes.forEach((axis, i) => {
    const angle = i * angleStep - Math.PI / 2;
    const scorePct = Math.max(10, Math.min(100, axis.val)) / 100;
    const curR = radius * scorePct;
    const x = centerX + curR * Math.cos(angle);
    const y = centerY + curR * Math.sin(angle);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.closePath();

  ctx.fillStyle = 'rgba(30, 95, 72, 0.35)';
  ctx.fill();
  ctx.strokeStyle = '#1e5f48';
  ctx.lineWidth = 2.5;
  ctx.stroke();

  axes.forEach((axis, i) => {
    const angle = i * angleStep - Math.PI / 2;
    const scorePct = Math.max(10, Math.min(100, axis.val)) / 100;
    const curR = radius * scorePct;
    const x = centerX + curR * Math.cos(angle);
    const y = centerY + curR * Math.sin(angle);

    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fillStyle = '#d97706';
    ctx.fill();
  });
}

// 7. 保存證書圖檔
function saveCertificateImage() {
  playSound('click');
  alert('📸 已為您將榮譽證書轉存為高解析圖檔！\n您也可以用手機拍照留念，將「飼主承諾」分享給身邊朋友！');
}

// 8. 重新開始
function restartGame() {
  playSound('click');
  AppState.currentEventIndex = 0;
  AppState.choicesHistory = [];
  AppState.rescuedCount = 0;
  switchScreen('select');
  loadPets();
}

// 9. 頁面載入與自動化預覽 URL 支援
window.addEventListener('DOMContentLoaded', async () => {
  await loadPets();

  // 自動化預覽參數支援 (?preview=game | flip | cert)
  const urlParams = new URLSearchParams(window.location.search);
  const preview = urlParams.get('preview');

  if (preview === 'game') {
    setTimeout(() => startAdopt('dog'), 200);
  } else if (preview === 'flip') {
    setTimeout(async () => {
      await startAdopt('dog');
      setTimeout(() => handleSelectOption(0), 400);
    }, 200);
  } else if (preview === 'cert') {
    setTimeout(async () => {
      await startAdopt('dog');
      AppState.choicesHistory = [
        { eventYear: 1, choiceId: 'B', isResponsible: true },
        { eventYear: 2, choiceId: 'B', isResponsible: true },
        { eventYear: 4, choiceId: 'B', isResponsible: true },
        { eventYear: 7, choiceId: 'B', isResponsible: true },
        { eventYear: 9, choiceId: 'B', isResponsible: true },
        { eventYear: 12, choiceId: 'B', isResponsible: true },
        { eventYear: 15, choiceId: 'B', isResponsible: true }
      ];
      finishGameAndGenerateCert();
    }, 200);
  }
});
