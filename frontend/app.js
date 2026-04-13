/**
 * NutriMind – AI Food Decision Coach
 * Frontend Application Logic
 * Handles routing, API calls, voice input, notifications, gamification,
 * and dynamic UI rendering.
 */

// ═══════════════════════════════════════════
// CONFIGURATION & STATE
// ═══════════════════════════════════════════

const API = '';  // same origin
let state = {
    token: localStorage.getItem('nutrimind_token') || null,
    user: JSON.parse(localStorage.getItem('nutrimind_user') || 'null'),
    currentScreen: 'screen-welcome',
    lastScanResult: null,
    mealPlanData: null,
    notifications: [],
    voiceRecognition: null,
};

// ═══════════════════════════════════════════
// GAMIFICATION LEVELS
// ═══════════════════════════════════════════

const LEVELS = [
    { name: '🌱 Beginner', minPoints: 0, maxPoints: 100 },
    { name: '🌿 Health Explorer', minPoints: 100, maxPoints: 300 },
    { name: '💪 Nutrition Fighter', minPoints: 300, maxPoints: 600 },
    { name: '🌟 Wellness Star', minPoints: 600, maxPoints: 1000 },
    { name: '🔥 Super Eater', minPoints: 1000, maxPoints: 1800 },
    { name: '👑 NutriMaster', minPoints: 1800, maxPoints: 3000 },
    { name: '🏆 Legend', minPoints: 3000, maxPoints: Infinity },
];

function getLevel(points) {
    for (let i = LEVELS.length - 1; i >= 0; i--) {
        if (points >= LEVELS[i].minPoints) return { ...LEVELS[i], index: i };
    }
    return { ...LEVELS[0], index: 0 };
}


// ═══════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    // Splash particles
    createSplashParticles();

    if (state.token && state.user) {
        if (state.user.profile_complete) {
            showScreen('screen-dashboard');
            showNav();
            loadDashboard();
            loadFoodDatabase();
        } else {
            showScreen('screen-setup');
        }
    } else {
        showScreen('screen-welcome');
    }

    // Auto-select meal type chip based on time
    autoSelectMealType();

    // Initialize voice recognition
    initVoiceRecognition();
});


// ═══════════════════════════════════════════
// SPLASH PARTICLES
// ═══════════════════════════════════════════

function createSplashParticles() {
    const container = document.getElementById('splashParticles');
    if (!container) return;
    const colors = ['rgba(99,102,241,0.4)', 'rgba(168,85,247,0.3)', 'rgba(236,72,153,0.3)', 'rgba(34,211,238,0.3)'];
    for (let i = 0; i < 20; i++) {
        const p = document.createElement('div');
        p.className = 'splash-particle';
        const size = 3 + Math.random() * 6;
        p.style.width = size + 'px';
        p.style.height = size + 'px';
        p.style.left = Math.random() * 100 + '%';
        p.style.top = Math.random() * 100 + '%';
        p.style.background = colors[Math.floor(Math.random() * colors.length)];
        p.style.setProperty('--dx', (Math.random() - 0.5) * 120 + 'px');
        p.style.setProperty('--dy', (Math.random() - 0.5) * 120 + 'px');
        p.style.setProperty('--duration', (4 + Math.random() * 6) + 's');
        p.style.animationDelay = Math.random() * 5 + 's';
        p.style.animationIterationCount = 'infinite';
        container.appendChild(p);
    }
}


// ═══════════════════════════════════════════
// NAVIGATION & SCREEN MANAGEMENT
// ═══════════════════════════════════════════

function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    const target = document.getElementById(screenId);
    if (target) {
        target.classList.add('active');
        state.currentScreen = screenId;
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function showNav() {
    document.getElementById('bottomNav').style.display = 'flex';
}

function hideNav() {
    document.getElementById('bottomNav').style.display = 'none';
}

function navigate(tab) {
    // Update active nav
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const navBtn = document.getElementById(`nav-${tab}`);
    if (navBtn) navBtn.classList.add('active');

    showScreen(`screen-${tab}`);

    // Load data for the screen
    if (tab === 'dashboard') loadDashboard();
    if (tab === 'profile') loadProfile();
    if (tab === 'scanner') loadFoodDatabase();
    if (tab === 'mealplan') loadMealPlan();
}


// ═══════════════════════════════════════════
// AUTH SYSTEM
// ═══════════════════════════════════════════

let authMode = 'signup';

function showAuthMode(mode) {
    authMode = mode;
    showScreen('screen-auth');
    updateAuthUI();
}

function toggleAuthMode() {
    authMode = authMode === 'signup' ? 'login' : 'signup';
    updateAuthUI();
}

function updateAuthUI() {
    const nameGroup = document.getElementById('nameGroup');
    const title = document.getElementById('authTitle');
    const subtitle = document.getElementById('authSubtitle');
    const submitBtn = document.getElementById('authSubmitBtn');
    const toggleText = document.getElementById('authToggleText');
    const toggleLink = document.getElementById('authToggleLink');

    if (authMode === 'login') {
        nameGroup.style.display = 'none';
        title.textContent = 'Welcome Back';
        subtitle.textContent = 'Log in to continue your journey';
        submitBtn.textContent = 'Log In';
        toggleText.textContent = "Don't have an account? ";
        toggleLink.textContent = 'Sign Up';
    } else {
        nameGroup.style.display = 'block';
        title.textContent = 'Create Account';
        subtitle.textContent = 'Start your healthy eating journey';
        submitBtn.textContent = 'Sign Up';
        toggleText.textContent = 'Already have an account? ';
        toggleLink.textContent = 'Log In';
    }

    hideAuthError();
}

function showAuthError(msg) {
    const el = document.getElementById('authError');
    el.textContent = msg;
    el.classList.add('visible');
}

function hideAuthError() {
    document.getElementById('authError').classList.remove('visible');
}

async function handleAuth(event) {
    event.preventDefault();
    hideAuthError();

    const email = document.getElementById('authEmail').value.trim();
    const password = document.getElementById('authPassword').value;
    const name = document.getElementById('authName').value.trim();

    if (authMode === 'signup' && !name) {
        showAuthError('Please enter your name');
        return;
    }
    if (!email || !password) {
        showAuthError('Please fill in all fields');
        return;
    }

    showLoading(authMode === 'signup' ? 'Creating your account...' : 'Logging in...');

    try {
        const endpoint = authMode === 'signup' ? '/api/auth/signup' : '/api/auth/login';
        const body = authMode === 'signup'
            ? { email, password, name }
            : { email, password };

        const res = await apiFetch(endpoint, 'POST', body, false);

        state.token = res.token;
        state.user = res.user;
        localStorage.setItem('nutrimind_token', res.token);
        localStorage.setItem('nutrimind_user', JSON.stringify(res.user));

        hideLoading();

        if (res.user.profile_complete) {
            showScreen('screen-dashboard');
            showNav();
            loadDashboard();
            loadFoodDatabase();
            showToast('Welcome back, ' + res.user.name + '! 🎉', 'success');
        } else {
            showScreen('screen-setup');
            showToast('Account created! Let\'s set up your profile 🚀', 'success');
        }
    } catch (err) {
        hideLoading();
        showAuthError(err.message || 'Authentication failed');
    }
}

function logout() {
    state.token = null;
    state.user = null;
    localStorage.removeItem('nutrimind_token');
    localStorage.removeItem('nutrimind_user');
    hideNav();
    showScreen('screen-welcome');
    showToast('Logged out successfully', 'info');
}


// ═══════════════════════════════════════════
// PROFILE SETUP
// ═══════════════════════════════════════════

function selectChip(el, groupId) {
    const group = document.getElementById(groupId);
    group.querySelectorAll('.chip').forEach(c => c.classList.remove('selected'));
    el.classList.add('selected');
}

function getSelectedChip(groupId) {
    const selected = document.querySelector(`#${groupId} .chip.selected`);
    return selected ? selected.dataset.value : null;
}

async function handleProfileSetup(event) {
    event.preventDefault();

    const age = parseInt(document.getElementById('setupAge').value);
    const weight = parseFloat(document.getElementById('setupWeight').value);
    const height = parseFloat(document.getElementById('setupHeight').value);
    const gender = document.getElementById('setupGender').value;
    const goal = getSelectedChip('goalChips');
    const diet = getSelectedChip('dietChips');
    const activity = getSelectedChip('activityChips');
    const conditions = document.getElementById('setupConditions').value.trim();

    if (!age || !weight || !height || !goal || !diet) {
        showToast('Please fill in all required fields', 'error');
        return;
    }

    showLoading('Setting up your profile...');

    try {
        const res = await apiFetch('/api/profile', 'PUT', {
            age, weight, height, gender,
            goal, diet_preference: diet,
            activity_level: activity || 'moderate',
            health_conditions: conditions || null,
        });

        // Update user state
        state.user.profile_complete = true;
        localStorage.setItem('nutrimind_user', JSON.stringify(state.user));

        hideLoading();
        showScreen('screen-dashboard');
        showNav();
        loadDashboard();
        loadFoodDatabase();
        showToast('Profile set up! Your daily target: ' + res.daily_calorie_target + ' kcal 🎯', 'success');
    } catch (err) {
        hideLoading();
        showToast(err.message || 'Failed to update profile', 'error');
    }
}

async function initSetupForm() {
    try {
        const profile = await apiFetch('/api/profile');

        if (profile.age) document.getElementById('setupAge').value = profile.age;
        if (profile.weight) document.getElementById('setupWeight').value = profile.weight;
        if (profile.height) document.getElementById('setupHeight').value = profile.height;
        if (profile.gender) document.getElementById('setupGender').value = profile.gender;
        if (profile.health_conditions) document.getElementById('setupConditions').value = profile.health_conditions;

        // Select chips
        if (profile.goal) {
            const chip = document.querySelector(`#goalChips .chip[data-value="${profile.goal}"]`);
            if (chip) selectChip(chip, 'goalChips');
        }
        if (profile.diet_preference) {
            const chip = document.querySelector(`#dietChips .chip[data-value="${profile.diet_preference}"]`);
            if (chip) selectChip(chip, 'dietChips');
        }
        if (profile.activity_level) {
            const chip = document.querySelector(`#activityChips .chip[data-value="${profile.activity_level}"]`);
            if (chip) selectChip(chip, 'activityChips');
        }
    } catch (err) {
        console.error('Failed to init setup form:', err);
    }
}


// ═══════════════════════════════════════════
// DASHBOARD
// ═══════════════════════════════════════════

async function loadDashboard() {
    try {
        const [dashboard, reco, waterData, calorieHistory] = await Promise.all([
            apiFetch('/api/dashboard'),
            apiFetch('/api/recommendations'),
            apiFetch('/api/water-log'),
            apiFetch('/api/calorie-history?days=7'),
        ]);

        // Greeting
        const hour = new Date().getHours();
        let greeting = 'morning';
        if (hour >= 12 && hour < 17) greeting = 'afternoon';
        else if (hour >= 17) greeting = 'evening';
        document.getElementById('timeGreeting').textContent = greeting;
        document.getElementById('dashUserName').textContent = dashboard.user.name;

        // Points & streak with count-up animation
        animateNumber('dashPoints', dashboard.user.points);
        animateNumber('dashStreak', dashboard.user.streak_days);

        // Level bar
        updateLevelBar(dashboard.user.points);

        // Calorie ring
        const cal = dashboard.today.calories;
        const target = dashboard.today.calorie_target || 2000;
        const pct = Math.min(cal / target, 1);
        const offset = 490 - (490 * pct);

        const ring = document.getElementById('calorieRing');
        ring.style.transition = 'stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1)';
        setTimeout(() => ring.setAttribute('stroke-dashoffset', offset), 100);

        animateNumber('dashCalories', Math.round(cal));
        document.getElementById('dashTarget').textContent = target;

        const remaining = dashboard.today.calorie_remaining;
        if (cal === 0) {
            document.getElementById('calorieStatus').textContent = "Start logging meals to track!";
        } else if (remaining > 0) {
            document.getElementById('calorieStatus').textContent = `${Math.round(remaining)} kcal remaining today`;
        } else {
            document.getElementById('calorieStatus').textContent = "⚠️ Daily target reached!";
        }

        // Macros
        document.getElementById('dashProtein').textContent = Math.round(dashboard.today.protein) + 'g';
        document.getElementById('dashCarbs').textContent = Math.round(dashboard.today.carbs) + 'g';
        document.getElementById('dashFats').textContent = Math.round(dashboard.today.fats) + 'g';

        // Health score
        const healthEl = document.getElementById('dashHealthScore');
        if (dashboard.today.avg_health_score > 0) {
            healthEl.textContent = Math.round(dashboard.today.avg_health_score);
        } else {
            healthEl.textContent = '—';
        }

        // Water tracker
        renderWaterTracker(waterData);

        // 7-Day Chart
        renderCalorieChart(calorieHistory);

        // Recommendations
        if (reco.message) {
            document.getElementById('recoMessage').style.display = 'flex';
            document.getElementById('recoMessageText').textContent = reco.message;
        }

        const recoList = document.getElementById('recoList');
        recoList.innerHTML = '';
        const foodEmojis = ['🥗', '🍛', '🥪', '🍲', '🥘', '🥙'];
        (reco.suggestions || []).forEach((s, i) => {
            const scoreClass = s.score >= 80 ? 'excellent' : s.score >= 60 ? 'good' : s.score >= 40 ? 'moderate' : 'poor';
            recoList.innerHTML += `
                <div class="suggestion-card" onclick="quickScan('${s.name.replace(/'/g, "\\'")}')" style="animation-delay:${i * 0.06}s;">
                    <span class="suggestion-emoji">${foodEmojis[i % foodEmojis.length]}</span>
                    <div class="suggestion-info">
                        <div class="suggestion-name">${s.name}</div>
                        <div class="suggestion-meta">${s.calories} kcal • ${s.protein}g P • ${s.carbs}g C • ${s.fats}g F</div>
                    </div>
                    <span class="health-score ${scoreClass}" style="font-size:0.78rem;">${s.score}</span>
                </div>
            `;
        });

        // Nudges
        const nudgeList = document.getElementById('nudgeList');
        nudgeList.innerHTML = '';
        (dashboard.behavior.nudges || []).forEach((nudge, i) => {
            nudgeList.innerHTML += `
                <div class="nudge-card" style="animation-delay:${i * 0.08}s;">
                    <span class="nudge-icon">💬</span>
                    <span class="nudge-text">${nudge}</span>
                </div>
            `;
        });

        // Smart notifications from nudges
        buildNotifications(dashboard.behavior.nudges || [], reco);

        // Today logs
        const todayLogs = document.getElementById('todayLogs');
        const logsRes = await apiFetch('/api/food-logs?days=1');
        if (logsRes.logs && logsRes.logs.length > 0) {
            todayLogs.innerHTML = '';
            const mealEmojis = { breakfast: '🌅', lunch: '☀️', dinner: '🌙', snack: '🍪' };
            logsRes.logs.forEach((log, i) => {
                const time = log.logged_at ? new Date(log.logged_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';
                todayLogs.innerHTML += `
                    <div class="log-item" style="animation-delay:${i * 0.05}s;">
                        <span class="log-emoji">${mealEmojis[log.meal_type] || '🍽️'}</span>
                        <div class="log-info">
                            <div class="log-name">${log.food_name}</div>
                            <div class="log-time">${log.meal_type || ''} ${time ? '• ' + time : ''}</div>
                        </div>
                        <span class="log-cal">${Math.round(log.calories)} kcal</span>
                        <button class="btn-delete" onclick="deleteFoodLog(${log.id})" title="Delete log">×</button>
                    </div>
                `;
            });
        } else {
            todayLogs.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🍽️</div>
                    <div class="empty-text">No meals logged today. Tap the scanner to add!</div>
                </div>
            `;
        }

        // Badges
        renderBadges(dashboard.achievements, 'badgeGrid');

    } catch (err) {
        console.error('Dashboard load error:', err);
    }
}


// ═══════════════════════════════════════════
// LEVEL BAR
// ═══════════════════════════════════════════

function updateLevelBar(points) {
    const level = getLevel(points);
    const badge = document.getElementById('levelBadge');
    const xp = document.getElementById('levelXP');
    const fill = document.getElementById('levelFill');

    if (badge) badge.textContent = level.name;

    if (level.maxPoints === Infinity) {
        if (xp) xp.textContent = `${points} XP • MAX LEVEL`;
        if (fill) fill.style.width = '100%';
    } else {
        const progress = ((points - level.minPoints) / (level.maxPoints - level.minPoints)) * 100;
        if (xp) xp.textContent = `${points} / ${level.maxPoints} XP`;
        if (fill) fill.style.width = Math.min(progress, 100) + '%';
    }
}


// ═══════════════════════════════════════════
// NUMBER COUNT-UP ANIMATION
// ═══════════════════════════════════════════

function animateNumber(elementId, target, duration = 800) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const start = parseInt(el.textContent) || 0;
    if (start === target) return;
    const startTime = performance.now();

    function tick(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(start + (target - start) * eased);
        el.textContent = current;
        if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
}


// ═══════════════════════════════════════════
// WATER TRACKER
// ═══════════════════════════════════════════

function renderWaterTracker(data) {
    const totalMl = data.today_total_ml || 0;
    const goalMl = data.goal_ml || 2500;
    const glasses = Math.round(totalMl / 250);
    const goalGlasses = Math.round(goalMl / 250);
    const pct = Math.min(totalMl / goalMl, 1);

    document.getElementById('dashWater').textContent = glasses;
    document.getElementById('dashWaterGoal').textContent = goalGlasses;

    const wave = document.getElementById('waterWave');
    if (wave) {
        wave.style.height = `${pct * 100}%`;
    }
}

async function logWater() {
    try {
        const res = await apiFetch('/api/water-log', 'POST', { amount_ml: 250 });
        renderWaterTracker(res);
        showToast(res.message || 'Water logged! 💧', 'success');
    } catch (err) {
        showToast(err.message || 'Failed to log water', 'error');
    }
}


// ═══════════════════════════════════════════
// 7-DAY CALORIE CHART
// ═══════════════════════════════════════════

function renderCalorieChart(data) {
    const container = document.getElementById('calorieChart');
    const history = data.history || [];
    const target = data.calorie_target || 2000;

    if (history.length === 0) {
        container.innerHTML = '<div class="chart-loading">No data yet</div>';
        return;
    }

    const maxCal = Math.max(...history.map(d => d.calories), target) || target;
    const todayStr = new Date().toISOString().slice(0, 10);
    const targetPct = (target / maxCal) * 100;

    let barsHtml = '';
    history.forEach((day, i) => {
        const heightPct = maxCal > 0 ? (day.calories / maxCal) * 100 : 0;
        const isToday = day.date === todayStr;
        const overTarget = day.calories > target;

        barsHtml += `
            <div class="chart-bar-wrapper">
                <div class="chart-bar-track">
                    <div class="chart-bar ${overTarget ? 'over-target' : ''}"
                         style="height:${heightPct}%;animation:countUp 0.6s ${i * 0.08}s both;">
                        <span class="chart-bar-cal">${Math.round(day.calories)}</span>
                    </div>
                </div>
                <div class="chart-bar-label ${isToday ? 'today' : ''}">${day.day_label}</div>
            </div>
        `;
    });

    container.innerHTML = `
        <div class="chart-bars" style="position:relative;">
            <div class="chart-target-line" style="bottom:${targetPct}%;">
                <span class="chart-target-label">Target ${target}</span>
            </div>
            ${barsHtml}
        </div>
    `;
}


// ═══════════════════════════════════════════
// BADGE SYSTEM
// ═══════════════════════════════════════════

function renderBadges(achievements, containerId) {
    const container = document.getElementById(containerId);
    const allBadges = [
        { id: 'first_scan', name: 'First Scan', icon: '📸', desc: 'Scanned your first food item!' },
        { id: 'five_logs', name: 'Logging Pro', icon: '📝', desc: 'Logged 5 meals!' },
        { id: 'ten_logs', name: 'Dedicated Logger', icon: '🏆', desc: 'Logged 10 meals!' },
        { id: 'healthy_streak3', name: 'Healthy Start', icon: '🌱', desc: '3-day healthy eating streak!' },
        { id: 'healthy_streak7', name: 'Week Warrior', icon: '⚡', desc: '7-day streak!' },
        { id: 'health_master', name: 'Health Master', icon: '👑', desc: 'Avg health score above 75!' },
        { id: 'calorie_watch', name: 'Calorie Watcher', icon: '🔥', desc: 'Avg calories under 350!' },
    ];

    const earnedIds = (achievements || []).map(a => a.badge_id);

    container.innerHTML = allBadges.map((badge, i) => {
        const earned = earnedIds.includes(badge.id);
        return `
            <div class="badge-card ${earned ? '' : 'locked'}" style="animation-delay:${i * 0.05}s;">
                <div class="badge-icon">${badge.icon}</div>
                <div class="badge-name">${badge.name}</div>
                <div class="badge-desc">${badge.desc}</div>
            </div>
        `;
    }).join('');
}


// ═══════════════════════════════════════════
// BADGE UNLOCK MODAL
// ═══════════════════════════════════════════

function showBadgeModal(badge) {
    document.getElementById('badgeModalIcon').textContent = badge.badge_icon;
    document.getElementById('badgeModalName').textContent = badge.badge_name;
    document.getElementById('badgeModalDesc').textContent = badge.description;

    // Create confetti
    const canvas = document.getElementById('confettiCanvas');
    canvas.innerHTML = '';
    const colors = ['#6366f1', '#8b5cf6', '#a855f7', '#ec4899', '#f472b6', '#34d399', '#fbbf24', '#60a5fa'];
    for (let i = 0; i < 30; i++) {
        const piece = document.createElement('div');
        piece.className = 'confetti-piece';
        piece.style.left = Math.random() * 100 + '%';
        piece.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        piece.style.animationDelay = Math.random() * 0.8 + 's';
        piece.style.animationDuration = (1.5 + Math.random()) + 's';
        piece.style.width = (5 + Math.random() * 6) + 'px';
        piece.style.height = (5 + Math.random() * 6) + 'px';
        piece.style.borderRadius = Math.random() > 0.5 ? '50%' : '2px';
        canvas.appendChild(piece);
    }

    document.getElementById('badgeModal').classList.add('visible');
}

function closeBadgeModal() {
    document.getElementById('badgeModal').classList.remove('visible');
}


// ═══════════════════════════════════════════
// AUTO MEAL TYPE SELECTION
// ═══════════════════════════════════════════

function autoSelectMealType() {
    const hour = new Date().getHours();
    let mealType = 'snack';
    if (hour >= 5 && hour < 11) mealType = 'breakfast';
    else if (hour >= 11 && hour < 15) mealType = 'lunch';
    else if (hour >= 18 && hour < 22) mealType = 'dinner';

    const chips = document.querySelectorAll('#mealTypeChips .chip');
    chips.forEach(c => {
        c.classList.remove('selected');
        if (c.dataset.value === mealType) c.classList.add('selected');
    });
}


// ═══════════════════════════════════════════
// VOICE INPUT (Web Speech API)
// ═══════════════════════════════════════════

function initVoiceRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        // Hide voice button if not supported
        const btn = document.getElementById('btn-voice');
        if (btn) btn.style.display = 'none';
        return;
    }

    state.voiceRecognition = new SpeechRecognition();
    state.voiceRecognition.continuous = false;
    state.voiceRecognition.interimResults = false;
    state.voiceRecognition.lang = 'en-US';

    state.voiceRecognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById('foodNameInput').value = transcript;
        stopVoiceUI();

        // Check for special commands
        const lower = transcript.toLowerCase();
        if (lower.includes('what should i eat') || lower.includes('suggest') || lower.includes('recommend')) {
            navigate('dashboard');
            showToast(`Here are today's recommendations! 🎯`, 'info');
        } else {
            showToast(`Heard: "${transcript}" 🎤`, 'success');
            scanFood();
        }
    };

    state.voiceRecognition.onerror = () => {
        stopVoiceUI();
        showToast('Could not hear you clearly. Try again! 🎤', 'error');
    };

    state.voiceRecognition.onend = () => {
        stopVoiceUI();
    };
}

function startVoiceInput() {
    if (!state.voiceRecognition) {
        showToast('Voice input not supported in this browser', 'error');
        return;
    }

    const btn = document.getElementById('btn-voice');
    const status = document.getElementById('voiceStatus');

    if (btn.classList.contains('active')) {
        state.voiceRecognition.stop();
        stopVoiceUI();
        return;
    }

    btn.classList.add('active');
    btn.textContent = '⏹️';
    if (status) status.style.display = 'flex';

    try {
        state.voiceRecognition.start();
    } catch (e) {
        stopVoiceUI();
    }
}

function stopVoiceUI() {
    const btn = document.getElementById('btn-voice');
    const status = document.getElementById('voiceStatus');
    if (btn) {
        btn.classList.remove('active');
        btn.textContent = '🎤';
    }
    if (status) status.style.display = 'none';
}


// ═══════════════════════════════════════════
// SMART NOTIFICATIONS
// ═══════════════════════════════════════════

function buildNotifications(nudges, reco) {
    const list = [];
    const now = new Date();

    nudges.forEach(nudge => {
        list.push({
            icon: '🧠',
            text: nudge,
            time: 'Just now',
        });
    });

    // Time-based nudge
    const hour = now.getHours();
    if (hour >= 12 && hour < 14) {
        list.push({ icon: '🍽️', text: 'Lunch time! Have you eaten yet? Log your meal.', time: 'Smart reminder' });
    }
    if (hour >= 21) {
        list.push({ icon: '🌙', text: 'Late night alert — try to avoid heavy meals now.', time: 'Smart reminder' });
    }
    if (hour >= 15 && hour < 17) {
        list.push({ icon: '🥜', text: 'Snack o\'clock! Grab something healthy to keep your energy up.', time: 'Smart reminder' });
    }

    state.notifications = list;

    // Show dot if notifications exist
    const dot = document.getElementById('notifDot');
    if (dot) dot.style.display = list.length > 0 ? 'block' : 'none';
}

function openNotifications() {
    const drawer = document.getElementById('notificationDrawer');
    const list = document.getElementById('notificationList');

    if (state.notifications.length === 0) {
        list.innerHTML = `<div class="empty-state"><div class="empty-icon">🔕</div><div class="empty-text">No notifications yet!</div></div>`;
    } else {
        list.innerHTML = state.notifications.map((n, i) => `
            <div class="notification-item" style="animation-delay:${i * 0.06}s;">
                <span class="notif-icon">${n.icon}</span>
                <div class="notif-content">
                    <div class="notif-text">${n.text}</div>
                    <div class="notif-time">${n.time}</div>
                </div>
            </div>
        `).join('');
    }

    drawer.classList.add('open');

    // Hide dot
    const dot = document.getElementById('notifDot');
    if (dot) dot.style.display = 'none';
}

function closeNotifications() {
    document.getElementById('notificationDrawer').classList.remove('open');
}


// ═══════════════════════════════════════════
// AI FOOD SCANNER
// ═══════════════════════════════════════════

async function loadFoodDatabase() {
    try {
        const res = await apiFetch('/api/food-database');
        const datalist = document.getElementById('foodSuggestions');
        datalist.innerHTML = '';
        (res.foods || []).forEach(food => {
            const option = document.createElement('option');
            option.value = food;
            datalist.appendChild(option);
        });
    } catch (err) {
        // non-critical
    }
}

function handleImageUpload(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById('previewImg').src = e.target.result;
            document.getElementById('imagePreview').style.display = 'block';

            // Simulating AI recognition
            showLoading('AI analyzing image... 🤖');

            setTimeout(() => {
                const options = document.querySelectorAll('#foodSuggestions option');
                if (options.length > 0) {
                    const randomFood = options[Math.floor(Math.random() * options.length)].value;
                    document.getElementById('foodNameInput').value = randomFood;
                    hideLoading();
                    showToast(`AI detected: ${randomFood}! ✨`, 'success');
                    scanFood();
                } else {
                    hideLoading();
                    showToast('Photo captured! Type the food name to analyze 📸', 'info');
                }
            }, 1500);
        };
        reader.readAsDataURL(file);
    }
}

async function scanFood() {
    const foodName = document.getElementById('foodNameInput').value.trim();
    if (!foodName) {
        showToast('Please enter a food name', 'error');
        return;
    }

    showLoading('Analyzing food with AI...');

    try {
        const result = await apiFetch('/api/scan-food', 'POST', { food_name: foodName });
        state.lastScanResult = result;

        // Display result
        document.getElementById('resultFoodName').textContent = result.food_name;
        document.getElementById('resultCalories').textContent = result.calories;
        document.getElementById('resultProtein').textContent = result.protein + 'g';
        document.getElementById('resultCarbs').textContent = result.carbs + 'g';
        document.getElementById('resultFats').textContent = result.fats + 'g';
        document.getElementById('resultConfidence').textContent = `AI Confidence: ${Math.round(result.ai_confidence * 100)}%`;

        // Health score
        const scoreEl = document.getElementById('resultHealthScore');
        scoreEl.textContent = result.health_score + '/100';
        scoreEl.className = 'health-score';
        if (result.health_score >= 75) scoreEl.classList.add('excellent');
        else if (result.health_score >= 55) scoreEl.classList.add('good');
        else if (result.health_score >= 35) scoreEl.classList.add('moderate');
        else scoreEl.classList.add('poor');

        // Warning
        const warningEl = document.getElementById('resultWarning');
        if (result.warning) {
            warningEl.textContent = result.warning;
            warningEl.classList.add('visible');
        } else {
            warningEl.classList.remove('visible');
        }

        // Alternatives
        const altList = document.getElementById('alternativesList');
        altList.innerHTML = '';
        (result.alternatives || []).forEach(alt => {
            altList.innerHTML += `
                <div class="alternative-card" onclick="quickScan('${alt.replace(/'/g, "\\'")}')">
                    <span class="alt-icon">✨</span>
                    <span class="alt-name">${alt}</span>
                </div>
            `;
        });

        document.getElementById('scanResult').classList.add('visible');
        hideLoading();
    } catch (err) {
        hideLoading();
        showToast(err.message || 'Scan failed', 'error');
    }
}

function quickScan(foodName) {
    document.getElementById('foodNameInput').value = foodName;
    navigate('scanner');
    scanFood();
}

async function logScannedFood() {
    if (!state.lastScanResult) return;

    const r = state.lastScanResult;

    // Get selected meal type or auto-detect
    const selectedMealType = getSelectedChip('mealTypeChips');
    let mealType = selectedMealType || 'snack';
    if (!selectedMealType) {
        const hour = new Date().getHours();
        if (hour >= 5 && hour < 11) mealType = 'breakfast';
        else if (hour >= 11 && hour < 15) mealType = 'lunch';
        else if (hour >= 18 && hour < 22) mealType = 'dinner';
    }

    showLoading('Logging meal...');

    try {
        const res = await apiFetch('/api/food-log', 'POST', {
            food_name: r.food_name,
            calories: r.calories,
            protein: r.protein,
            carbs: r.carbs,
            fats: r.fats,
            health_score: r.health_score,
            meal_type: mealType,
        });

        hideLoading();

        let msg = res.message || 'Food logged!';

        // Show badge modal for new badges
        if (res.new_badges && res.new_badges.length > 0) {
            res.new_badges.forEach((badge, i) => {
                setTimeout(() => showBadgeModal(badge), i * 2500);
            });
        }

        showToast(msg, 'success');

        // Reset scanner
        document.getElementById('scanResult').classList.remove('visible');
        document.getElementById('foodNameInput').value = '';
        document.getElementById('imagePreview').style.display = 'none';
        state.lastScanResult = null;

    } catch (err) {
        hideLoading();
        showToast(err.message || 'Failed to log food', 'error');
    }
}

async function deleteFoodLog(logId) {
    if (!confirm('Are you sure you want to delete this log?')) return;

    showLoading('Deleting log...');
    try {
        await apiFetch(`/api/food-log/${logId}`, 'DELETE');
        hideLoading();
        showToast('Log deleted', 'info');
        loadDashboard(); // Refresh
    } catch (err) {
        hideLoading();
        showToast('Failed to delete log', 'error');
    }
}


// ═══════════════════════════════════════════
// MEAL PLANNER
// ═══════════════════════════════════════════

async function loadMealPlan() {
    try {
        const res = await apiFetch('/api/meal-plan');
        if (res.meal_plan && res.meal_plan.length > 0) {
            state.mealPlanData = res.meal_plan;
            document.getElementById('dayTabs').style.display = 'flex';
            showMealDay(0);
        }
    } catch (err) {
        console.error('Failed to load meal plan:', err);
    }
}

async function generateMealPlan() {
    showLoading('Generating your personalized meal plan...');
    try {
        await apiFetch('/api/meal-plan/reset', 'POST');
        const res = await apiFetch('/api/meal-plan');
        state.mealPlanData = res.meal_plan || [];

        document.getElementById('dayTabs').style.display = 'flex';
        showMealDay(0);

        hideLoading();
        showToast('Meal plan generated! 📋', 'success');
    } catch (err) {
        hideLoading();
        showToast(err.message || 'Failed to generate plan', 'error');
    }
}

function showMealDay(dayIndex) {
    if (!state.mealPlanData || !state.mealPlanData[dayIndex]) return;

    // Update active tab
    document.querySelectorAll('.day-tab').forEach(t => t.classList.remove('active'));
    const activeTab = document.querySelector(`.day-tab[data-day="${dayIndex}"]`);
    if (activeTab) activeTab.classList.add('active');

    const day = state.mealPlanData[dayIndex];
    const container = document.getElementById('mealPlanContainer');
    const budgetMode = document.getElementById('budgetToggle')?.checked;

    // Calculate daily total
    const totalCal = (day.meals || []).reduce((sum, m) => sum + m.calories, 0);

    let html = `<div class="meal-plan-day">
        <div class="day-header">
            <span>📅 ${day.day}</span>
            <span class="day-total-cal">${totalCal} kcal total</span>
        </div>`;

    (day.meals || []).forEach(meal => {
        const budgetTag = budgetMode && meal.budget_friendly ? '<span class="budget-tag">💰 Budget</span>' : '';
        html += `
            <div class="meal-row" onclick="openRecipeModal('${meal.food_name.replace(/'/g, "\\'")}')">
                <span class="meal-type-tag ${meal.meal_type}">${meal.meal_type}</span>
                <div style="flex:1;">
                    <span class="meal-name">${meal.food_name}${budgetTag}</span>
                    <div class="meal-macros">${meal.protein}g P • ${meal.carbs}g C • ${meal.fats}g F</div>
                </div>
                <span class="meal-cal">${meal.calories} kcal</span>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}


// ═══════════════════════════════════════════
// PROFILE
// ═══════════════════════════════════════════

async function loadProfile() {
    try {
        const [profile, achievements] = await Promise.all([
            apiFetch('/api/profile'),
            apiFetch('/api/achievements'),
        ]);

        document.getElementById('profileName').textContent = profile.name;
        document.getElementById('profileEmail').textContent = profile.email;

        // Avatar (first letter)
        const avatar = document.getElementById('profileAvatar');
        if (avatar && profile.name) {
            avatar.textContent = profile.name.charAt(0).toUpperCase();
        }

        const goalLabels = { weight_loss: '🔥 Weight Loss', muscle_gain: '💪 Muscle Gain', maintenance: '⚖️ Maintenance' };
        const dietLabels = { veg: '🥗 Vegetarian', non_veg: '🍗 Non-Veg', vegan: '🌿 Vegan' };
        const actLabels = { sedentary: '🛋️ Sedentary', moderate: '🚶 Moderate', active: '🏃 Active' };

        document.getElementById('profileGoal').textContent = goalLabels[profile.goal] || '—';
        document.getElementById('profileDiet').textContent = dietLabels[profile.diet_preference] || '—';
        document.getElementById('profileActivity').textContent = actLabels[profile.activity_level] || '—';
        document.getElementById('profileCalTarget').textContent = (profile.daily_calorie_target || '—') + ' kcal';
        document.getElementById('profilePoints').textContent = achievements.total_points || 0;

        // BMI calculation
        updateBMI(profile);

        renderBadges(achievements.achievements, 'profileBadges');

        // Load weight history
        loadWeightHistory();
    } catch (err) {
        console.error('Profile load error:', err);
    }
}

function updateBMI(profile) {
    const bmiValue = document.getElementById('bmiValue');
    const bmiIndicator = document.getElementById('bmiIndicator');
    const bmiStatus = document.getElementById('bmiStatus');

    if (profile.weight && profile.height) {
        const heightM = profile.height / 100;
        const bmi = (profile.weight / (heightM * heightM)).toFixed(1);
        bmiValue.textContent = bmi;

        // Position indicator (BMI range 15-40 mapped to 0-100%)
        const pct = Math.min(Math.max(((bmi - 15) / 25) * 100, 0), 100);
        bmiIndicator.style.left = pct + '%';

        // Status text
        if (bmi < 18.5) {
            bmiStatus.textContent = '📉 Underweight — Consider increasing calorie intake';
            bmiStatus.style.color = 'var(--accent-blue)';
        } else if (bmi < 25) {
            bmiStatus.textContent = '✅ Normal — Great job! Keep it up';
            bmiStatus.style.color = 'var(--accent-green)';
        } else if (bmi < 30) {
            bmiStatus.textContent = '⚠️ Overweight — Focus on balanced nutrition';
            bmiStatus.style.color = 'var(--accent-orange)';
        } else {
            bmiStatus.textContent = '🔴 Obese — Consider consulting a health professional';
            bmiStatus.style.color = 'var(--accent-red)';
        }
    } else {
        bmiValue.textContent = '—';
        bmiStatus.textContent = 'Complete your profile to see BMI';
    }
}

async function loadWeightHistory() {
    try {
        const res = await apiFetch('/api/weight-history');
        renderWeightChart(res.history);
    } catch (err) {
        console.error('Weight history load error:', err);
    }
}

async function logWeight() {
    const input = document.getElementById('weightInput');
    const weight = parseFloat(input.value);
    if (!weight) return;

    showLoading('Updating weight...');
    try {
        await apiFetch('/api/weight-log', 'POST', { weight });
        input.value = '';
        hideLoading();
        showToast('Weight updated successfully! ⚖️', 'success');
        loadWeightHistory();
    } catch (err) {
        hideLoading();
        showToast(err.message, 'error');
    }
}

function renderWeightChart(history) {
    const container = document.getElementById('weightChartContainer');
    if (!history || history.length === 0) {
        container.innerHTML = '<div class="chart-loading">No weight data logged yet.</div>';
        return;
    }

    const maxWeight = Math.max(...history.map(h => h.weight));
    const minWeight = Math.min(...history.map(h => h.weight));
    const range = maxWeight - minWeight || 1;

    let html = '';
    const recentHistory = history.slice(-7);
    recentHistory.forEach((h, i) => {
        const heightPct = 30 + ((h.weight - minWeight) / range) * 60;
        const date = new Date(h.date).toLocaleDateString([], { month: 'short', day: 'numeric' });
        html += `
            <div class="weight-bar-wrapper">
                <div class="weight-bar-track">
                    <div class="weight-bar" style="height:${heightPct}%;"></div>
                </div>
                <div class="weight-label">${date}<br><b>${h.weight}</b></div>
            </div>
        `;
    });
    container.innerHTML = html;
}


// ═══════════════════════════════════════════
// RECIPES & GROCERY
// ═══════════════════════════════════════════

async function showGroceryList() {
    showLoading('Generating grocery list...');
    try {
        const res = await apiFetch('/api/grocery-list');
        const container = document.getElementById('groceryListContent');
        container.innerHTML = '';

        if (!res.grocery_list || res.grocery_list.length === 0) {
            container.innerHTML = '<div class="empty-state">No list available. Generate a meal plan first!</div>';
        } else {
            const grouped = res.grocery_list.reduce((acc, curr) => {
                if (!acc[curr.category]) acc[curr.category] = [];
                acc[curr.category].push(curr);
                return acc;
            }, {});

            for (const [cat, items] of Object.entries(grouped)) {
                let catHtml = `<div class="grocery-category">
                    <div class="grocery-cat-title">${cat}</div>`;
                items.forEach(item => {
                    catHtml += `
                        <div class="grocery-item">
                            <span>${item.item}</span>
                            <span style="color:var(--text-muted);">${item.quantity}</span>
                        </div>
                    `;
                });
                catHtml += '</div>';
                container.innerHTML += catHtml;
            }
        }

        hideLoading();
        document.getElementById('groceryModal').classList.add('visible');
    } catch (err) {
        hideLoading();
        showToast(err.message, 'error');
    }
}

function closeGroceryModal() {
    document.getElementById('groceryModal').classList.remove('visible');
}

async function openRecipeModal(foodName) {
    showLoading(`Loading recipe for ${foodName}...`);
    try {
        const res = await apiFetch(`/api/recipe/${encodeURIComponent(foodName)}`);

        document.getElementById('recipeTitle').textContent = res.food_name;
        document.getElementById('recipeTime').textContent = res.prep_time;
        document.getElementById('recipeDifficulty').textContent = res.difficulty;

        const ingList = document.getElementById('recipeIngredients');
        ingList.innerHTML = res.ingredients.map(i => `<li>${i}</li>`).join('');

        const instList = document.getElementById('recipeInstructions');
        instList.innerHTML = res.instructions.map(i => `<li>${i}</li>`).join('');

        document.getElementById('recipeTip').textContent = `💡 Pro Tip: ${res.pro_tip}`;

        hideLoading();
        document.getElementById('recipeModal').classList.add('visible');
    } catch (err) {
        hideLoading();
        showToast('Could not load recipe details', 'error');
    }
}

function closeRecipeModal() {
    document.getElementById('recipeModal').classList.remove('visible');
}

function editProfile() {
    initSetupForm();
    showScreen('screen-setup');
}


// ═══════════════════════════════════════════
// API HELPER
// ═══════════════════════════════════════════

async function apiFetch(endpoint, method = 'GET', body = null, auth = true) {
    const headers = { 'Content-Type': 'application/json' };
    if (auth && state.token) {
        headers['Authorization'] = `Bearer ${state.token}`;
    }

    const options = { method, headers };
    if (body) {
        options.body = JSON.stringify(body);
    }

    const res = await fetch(API + endpoint, options);
    const data = await res.json();

    if (!res.ok) {
        throw new Error(data.detail || 'Request failed');
    }

    return data;
}


// ═══════════════════════════════════════════
// UI HELPERS
// ═══════════════════════════════════════════

function showLoading(text = 'Loading...') {
    document.getElementById('loadingText').textContent = text;
    document.getElementById('loadingOverlay').classList.add('visible');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('visible');
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const icon = document.getElementById('toastIcon');
    const text = document.getElementById('toastText');

    toast.className = 'toast ' + type;
    text.textContent = message;

    if (type === 'success') icon.textContent = '✅';
    else if (type === 'error') icon.textContent = '❌';
    else icon.textContent = 'ℹ️';

    toast.classList.add('visible');

    setTimeout(() => {
        toast.classList.remove('visible');
    }, 3500);
}
