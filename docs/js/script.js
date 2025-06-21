let sessionsData = {};
let currentDay = 'Day 1';

// デバッグモード設定
const DEBUG_MODE = false; // true: デバッグログ表示, false: ログ非表示

// テストモード設定（アクティブセッション表示テスト用）
const TEST_ACTIVE_SESSION = false; // true: テスト用アクティブセッション表示, false: 実際の日時判定

// デバッグログ関数
function debugLog(category, message, ...args) {
    if (DEBUG_MODE) {
        const timestamp = new Date().toLocaleTimeString('ja-JP');
        console.log(`[${timestamp}][${category}] ${message}`, ...args);
    }
}

// デバッグログ（区切り線）
function debugSeparator() {
    if (DEBUG_MODE) {
        console.log('='.repeat(50));
    }
}

// セッションデータを読み込み
async function loadSessions() {
    try {
        const response = await fetch('sessions.json');
        if (!response.ok) {
            throw new Error('セッションデータの読み込みに失敗しました');
        }
        sessionsData = await response.json();
        renderCalendar();
    } catch (error) {
        document.getElementById('calendar-body').innerHTML = 
            '<div class="error">エラー: ' + error.message + '</div>';
    }
}

// カレンダーをレンダリング
function renderCalendar() {
    const calendarBody = document.getElementById('calendar-body');
    const stages = ['AWS Village Stage', 'Developers on Live', 'Community Stage'];
    
    // 表示用時間スロット（30分刻み）
    const displayTimeSlots = [];
    for (let hour = 11; hour <= 18; hour++) {
        displayTimeSlots.push(`${hour}:00`);
        if (hour < 18) {
            displayTimeSlots.push(`${hour}:30`);
        }
    }

    let html = '<div class="time-column">';
    displayTimeSlots.forEach(time => {
        html += `<div class="time-slot">${time}</div>`;
    });
    html += '</div>';

    // 各ステージのカラムを生成
    stages.forEach(stage => {
        html += '<div class="stage-column" style="position: relative;">';
        
        // 基本的な時間スロット（表示用、30分刻み）
        displayTimeSlots.forEach((time, index) => {
            html += `<div class="session-slot" data-time="${time}" data-stage="${stage}"></div>`;
        });
        
        // このステージの全セッションを取得してオーバーレイとして配置
        const sessions = sessionsData[stage]?.[currentDay] || [];
        
        // セッションを時間順にソート
        sessions.sort((a, b) => {
            const aStart = parseTime(a.time.split(' - ')[0]);
            const bStart = parseTime(b.time.split(' - ')[0]);
            return aStart - bStart;
        });
        
        sessions.forEach((session, index) => {
            const [startTime, endTime] = session.time.split(' - ');
            
            // 開始時間を基準時間（11:00）からの分数で計算
            const baseTime = parseTime('11:00');
            const sessionStartMinutes = parseTime(startTime);
            const minutesFromBase = sessionStartMinutes - baseTime;
            
            // 前のセッションとの重複チェック
            let topOffset = 2; // 基本の上マージン
            if (index > 0) {
                const prevSession = sessions[index - 1];
                const prevEndTime = prevSession.time.split(' - ')[1];
                const prevEndMinutes = parseTime(prevEndTime);
                
                // 前のセッションの終了時間と現在のセッションの開始時間が同じ、または重複している場合
                if (prevEndMinutes >= sessionStartMinutes) {
                    topOffset = 4; // マージンを増やす
                }
            }
            
            // 30分刻みの表示スロットでの位置を計算
            const top = (minutesFromBase / 30) * 80 + topOffset;
            
            const duration = calculateDurationInMinutes(session.time);
            // 高さからマージン分を差し引く
            const height = Math.max((duration / 30) * 80 - (topOffset + 2), 50); // 最小50px
            
            // デバッグログ
            if (stage === 'AWS Village Stage' && currentDay === 'Day 1') {
                debugLog('セッション配置', `${session.time}: start=${sessionStartMinutes}, top=${top}px, height=${height}px, offset=${topOffset}px`);
            }
            
            // セッションがアクティブかどうかを判定
            const isActive = isSessionActive(session.time, currentDay);
            const activeClass = isActive ? ' active-session' : '';
            
            html += `
                <div class="session${activeClass}" style="height: ${height}px; top: ${top}px; position: absolute; left: 8px; right: 8px; z-index: 10;" 
                     onclick="showSessionDetail('${stage}', '${session.time}', '${currentDay}')">
                    <div class="session-time">${session.time}</div>
                    <div class="session-title">${session.title}</div>
                    <div class="session-speaker">${getSpeakerName(session.speaker)}</div>
                </div>
            `;
        });
        
        html += '</div>';
    });

    calendarBody.innerHTML = html;
}

// セッションの継続時間を分で計算
function calculateDurationInMinutes(timeRange) {
    const [start, end] = timeRange.split(' - ');
    const startTime = parseTime(start);
    const endTime = parseTime(end);
    return endTime - startTime;
}

// 時間文字列を分に変換
function parseTime(timeStr) {
    const [hour, minute] = timeStr.split(':').map(Number);
    return hour * 60 + minute;
}

// 発表者名を短縮
function getSpeakerName(speaker) {
    if (!speaker || speaker === '未定') return '未定';
    
    // 複数発表者を改行で分割
    const lines = speaker.split('\n').filter(line => line.trim());
    const names = [];
    
    lines.forEach(line => {
        line = line.trim();
        if (!line) return;
        
        // AWSの部署名を除去して人名のみ抽出
        // パターン1: "AWS 部署名 氏名" の形式
        let match = line.match(/AWS[^　]*　(.+)/);
        if (match) {
            names.push(match[1].trim());
            return;
        }
        
        // パターン2: "Amazon 部署名 氏名" の形式
        match = line.match(/Amazon[^　]*　(.+)/);
        if (match) {
            names.push(match[1].trim());
            return;
        }
        
        // パターン3: "会社名 氏名" の形式
        match = line.match(/^[^　]+　(.+)/);
        if (match) {
            names.push(match[1].trim());
            return;
        }
        
        // パターン4: 最後の2つの単語を名前として抽出
        const words = line.split(/\s+/);
        if (words.length >= 2) {
            names.push(words.slice(-2).join(' '));
        } else {
            names.push(line);
        }
    });
    
    // 複数名の場合は改行で区切って表示、単一の場合はそのまま
    if (names.length > 1) {
        return names.join('\n');
    } else if (names.length === 1) {
        return names[0];
    } else {
        return speaker.split('\n')[0];
    }
}

// セッション詳細を表示
function showSessionDetail(stage, time, day) {
    const sessions = sessionsData[stage]?.[day] || [];
    const session = sessions.find(s => s.time === time);
    
    if (!session) return;

    // 現在のステージを記録
    currentModalStage = stage;

    document.getElementById('modal-time').textContent = session.time;
    document.getElementById('modal-title').textContent = session.title;
    document.getElementById('modal-description').textContent = session.description || 'セッション概要は準備中です。';
    
    // 発表者情報を複数行対応で設定
    const speakerElement = document.getElementById('modal-speaker');
    const speakerText = session.speaker || '未定';
    
    // 改行文字を<br>タグに変換して表示
    if (speakerText.includes('\n')) {
        speakerElement.innerHTML = speakerText.replace(/\n/g, '<br>');
    } else {
        speakerElement.textContent = speakerText;
    }
    
    // Googleカレンダー追加ボタンのイベント設定
    const addToCalendarBtn = document.getElementById('add-to-calendar');
    addToCalendarBtn.onclick = () => addToGoogleCalendar(session, day);
    
    document.getElementById('sessionModal').style.display = 'block';
}

// Googleカレンダーに追加
function addToGoogleCalendar(session, day) {
    const date = day === 'Day 1' ? '20250625' : '20250626';
    const [startTime, endTime] = session.time.split(' - ');
    
    const startDateTime = `${date}T${startTime.replace(':', '')}00`;
    const endDateTime = `${date}T${endTime.replace(':', '')}00`;
    
    const title = encodeURIComponent(session.title);
    
    // 現在表示中のステージを取得（モーダルのタイトルから推測）
    const currentStage = getCurrentStageFromModal();
    const description = encodeURIComponent(
        `【${currentStage}】\n${session.description}\n\n発表者:\n${session.speaker}\n\nAWS Summit Japan 2025`
    );
    const location = encodeURIComponent('幕張メッセ');
    
    const googleCalendarUrl = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&dates=${startDateTime}/${endDateTime}&details=${description}&location=${location}`;
    
    window.open(googleCalendarUrl, '_blank');
}

// 現在のステージ名を取得（セッション詳細表示時に使用）
let currentModalStage = '';

function getCurrentStageFromModal() {
    return currentModalStage;
}

// 日付切り替え
document.querySelectorAll('.day-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.day-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentDay = btn.dataset.day;
        renderCalendar();
        // Day切り替え後にアクティブセッションを更新
        setTimeout(updateActiveSessionsDisplay, 100);
    });
});

// モーダルを閉じる
document.querySelector('.close').addEventListener('click', () => {
    document.getElementById('sessionModal').style.display = 'none';
});

window.addEventListener('click', (event) => {
    const modal = document.getElementById('sessionModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});

// セッションがアクティブ（現在進行中）かどうかを判定
function isSessionActive(sessionTime, day) {
    // テストモードの場合、特定のセッションをアクティブとして表示
    if (TEST_ACTIVE_SESSION) {
        // 13:00-13:20のセッションをアクティブとしてテスト表示
        if (sessionTime && sessionTime.includes('13:00 - 13:20')) {
            return true;
        }
    }
    
    const now = new Date();
    const currentDate = now.toDateString();
    
    // 開催日の判定
    const summitDay1 = new Date('2025-06-25').toDateString();
    const summitDay2 = new Date('2025-06-26').toDateString();
    
    let targetDate = '';
    if (day === 'Day 1') {
        targetDate = summitDay1;
    } else if (day === 'Day 2') {
        targetDate = summitDay2;
    }
    
    // デバッグログ: 日付判定
    debugLog('日付判定', `現在日付: ${currentDate}, 対象日付: ${targetDate}, Day: ${day}`);
    
    // 現在日付が対象日でない場合はアクティブではない
    if (currentDate !== targetDate) {
        debugLog('日付判定', '日付不一致のためアクティブではない');
        return false;
    }
    
    // セッション時間の解析
    const [startTime, endTime] = sessionTime.split(' - ');
    const sessionStartMinutes = parseTime(startTime);
    const sessionEndMinutes = parseTime(endTime);
    
    // 現在時刻の分数変換
    const currentMinutes = now.getHours() * 60 + now.getMinutes();
    
    // デバッグログ: 時刻判定
    debugLog('時刻判定', `セッション: ${sessionTime}`);
    debugLog('時刻判定', `開始: ${startTime} (${sessionStartMinutes}分), 終了: ${endTime} (${sessionEndMinutes}分)`);
    debugLog('時刻判定', `現在: ${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')} (${currentMinutes}分)`);
    
    // セッション開始時刻 <= 現在時刻 < セッション終了時刻
    const isActive = currentMinutes >= sessionStartMinutes && currentMinutes < sessionEndMinutes;
    
    debugLog('判定結果', `${sessionTime} → ${isActive ? 'アクティブ' : '非アクティブ'}`);
    debugLog('判定結果', '---');
    
    return isActive;
}

// 現在時刻と開催状況を更新
function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('ja-JP', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    // デバッグログ: 現在時刻
    debugLog('現在時刻更新', `${now.toLocaleString('ja-JP')} (${now.toDateString()})`);
    
    // 時計の絵文字付きで表示
    document.getElementById('current-time').textContent = `🕐 ${timeString}`;
    
    // サミット開催状況の判定
    const currentDate = now.toDateString();
    const summitDay1 = new Date('2025-06-25').toDateString();
    const summitDay2 = new Date('2025-06-26').toDateString();
    const currentHour = now.getHours();
    
    let status = '';
    let statusClass = '';
    
    // デバッグログ: 開催状況判定
    debugLog('開催状況判定', `現在日付: ${currentDate}`);
    debugLog('開催状況判定', `Day1日付: ${summitDay1}`);
    debugLog('開催状況判定', `Day2日付: ${summitDay2}`);
    debugLog('開催状況判定', `現在時刻: ${currentHour}時`);
    
    if (currentDate === summitDay1 || currentDate === summitDay2) {
        // 開催日の場合、時間で判定
        if (currentHour < 11) {
            status = '📅 開催前';
            statusClass = 'before';
        } else if (currentHour >= 11 && currentHour < 19) {
            status = '🔴 開催中';
            statusClass = 'active';
        } else {
            status = '✅ 本日終了';
            statusClass = 'ended';
        }
        debugLog('開催状況判定', `開催日 → ${status}`);
    } else {
        // 開催日以外の場合
        const summitStart = new Date('2025-06-25');
        const summitEnd = new Date('2025-06-26');
        
        if (now < summitStart) {
            status = '📅 開催前';
            statusClass = 'before';
        } else if (now > summitEnd) {
            status = '✅ 開催終了';
            statusClass = 'ended';
        } else {
            status = '📅 開催期間';
            statusClass = 'active';
        }
        debugLog('開催状況判定', `開催日以外 → ${status}`);
    }
    
    const statusElement = document.getElementById('summit-status');
    statusElement.textContent = status;
    statusElement.className = `summit-status ${statusClass}`;
    
    // アクティブセッションの更新
    debugLog('アクティブセッション更新開始', `現在表示: ${currentDay}`);
    updateActiveSessionsDisplay();
}

// アクティブセッションの表示を更新
function updateActiveSessionsDisplay() {
    debugLog('アクティブセッション更新', '開始');
    
    // 開催日・開催時間帯の判定
    const now = new Date();
    const currentDate = now.toDateString();
    const summitDay1 = new Date('2025-06-25').toDateString();
    const summitDay2 = new Date('2025-06-26').toDateString();
    const currentHour = now.getHours();
    
    // 開催日以外はスキップ
    if (currentDate !== summitDay1 && currentDate !== summitDay2) {
        debugLog('アクティブセッション更新', `開催日以外のためスキップ (現在: ${currentDate})`);
        return;
    }
    
    // 開催時間外（11:00-19:00以外）はスキップ
    if (currentHour < 11 || currentHour >= 19) {
        debugLog('アクティブセッション更新', `開催時間外のためスキップ (現在: ${currentHour}時)`);
        return;
    }
    
    debugLog('アクティブセッション更新', '開催日・開催時間内のため判定実行');
    
    // 全てのセッション要素からactive-sessionクラスを削除
    const allSessions = document.querySelectorAll('.session');
    debugLog('アクティブセッション更新', `全セッション数: ${allSessions.length}`);
    
    allSessions.forEach(sessionElement => {
        sessionElement.classList.remove('active-session');
    });
    
    // 現在表示中の日のアクティブセッションを検索
    const stages = ['AWS Village Stage', 'Developers on Live', 'Community Stage'];
    let activeSessionCount = 0;
    
    stages.forEach(stage => {
        const sessions = sessionsData[stage]?.[currentDay] || [];
        debugLog('アクティブセッション更新', `${stage} (${currentDay}): ${sessions.length}セッション`);
        
        sessions.forEach(session => {
            if (isSessionActive(session.time, currentDay)) {
                activeSessionCount++;
                debugLog('アクティブセッション発見', `${stage}: ${session.time} - ${session.title}`);
                
                // 該当するセッション要素を検索してクラスを追加
                const sessionElements = document.querySelectorAll('.session');
                sessionElements.forEach(element => {
                    const timeElement = element.querySelector('.session-time');
                    const titleElement = element.querySelector('.session-title');
                    if (timeElement && titleElement && 
                        timeElement.textContent === session.time && 
                        titleElement.textContent === session.title) {
                        element.classList.add('active-session');
                        debugLog('アクティブセッション適用', 'DOM要素にactive-sessionクラスを追加');
                    }
                });
            }
        });
    });
    
    debugLog('アクティブセッション更新', `完了 - アクティブセッション数: ${activeSessionCount}`);
    debugSeparator();
}

// 現在の日付に基づいてDay1/Day2を自動選択
function autoSelectDay() {
    const now = new Date();
    const summitDay2 = new Date('2025-06-26');
    
    // 2025/6/26の場合はDay2、それ以外はDay1
    if (now.toDateString() === summitDay2.toDateString()) {
        currentDay = 'Day 2';
    } else {
        currentDay = 'Day 1';
    }
    
    // ボタンの状態を更新
    updateDayButtons();
}

// Day切り替えボタンの状態を更新
function updateDayButtons() {
    document.querySelectorAll('.day-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.day === currentDay) {
            btn.classList.add('active');
        }
    });
}

// 初期化
autoSelectDay(); // 自動選択を最初に実行
updateCurrentTime(); // 初回時刻更新
loadSessions();

// 1秒ごとに時刻を更新
setInterval(updateCurrentTime, 1000);

// トップに戻るボタンの機能
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// スクロール時のトップに戻るボタンとフッターヘッダー表示制御
window.addEventListener('scroll', () => {
    const backToTopBtn = document.getElementById('backToTop');
    const footerHeader = document.getElementById('footer-header');
    const calendarContainer = document.querySelector('.calendar-container');
    
    // トップに戻るボタンの表示制御
    if (window.pageYOffset > 300) {
        backToTopBtn.classList.add('show');
    } else {
        backToTopBtn.classList.remove('show');
    }
    
    // フッターヘッダーの表示制御
    if (calendarContainer) {
        const containerRect = calendarContainer.getBoundingClientRect();
        const calendarHeader = document.querySelector('.calendar-header');
        const headerRect = calendarHeader ? calendarHeader.getBoundingClientRect() : null;
        
        // カレンダーヘッダーが画面上部から見えなくなったらフッターヘッダーを表示
        if (headerRect && headerRect.bottom < 0) {
            footerHeader.style.display = 'grid';
            document.body.classList.add('footer-header-visible');
        } else {
            footerHeader.style.display = 'none';
            document.body.classList.remove('footer-header-visible');
        }
    }
});
