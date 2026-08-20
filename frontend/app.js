document.addEventListener('DOMContentLoaded', () => {
    // API client base URL is empty for relative paths (working with mounted app)
    const API_BASE = "";

    // DOM Elements
    const welcomeScreen = document.getElementById('welcome-screen');
    const selectorScreen = document.getElementById('selector-screen');
    const creationScreen = document.getElementById('creation-screen');
    const authModal = document.getElementById('auth-modal');
    const settingsModal = document.getElementById('settings-modal');
    const chatContainerWrap = document.getElementById('chat-container-wrap');

    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatContainer = document.getElementById('chat-container');
    const sendBtn = document.getElementById('send-btn');

    // Onboarding welcome controls
    const btnStartCreate = document.getElementById('btn-start-create');
    const btnCreateBack = document.getElementById('btn-create-back');

    // Selection Grid
    const profilesGrid = document.getElementById('profiles-grid');

    // Auth Form
    const authForm = document.getElementById('auth-form');
    const authPinInput = document.getElementById('auth-pin-input');
    const authProfileName = document.getElementById('auth-profile-name');
    const authRememberCheck = document.getElementById('auth-remember-check');
    const btnAuthCancel = document.getElementById('btn-auth-cancel');

    // Profile Settings Form
    const settingsForm = document.getElementById('settings-form');
    const btnSettingsClose = document.getElementById('btn-settings-close');
    const btnOpenSettings = document.getElementById('btn-open-settings');
    const btnSwitchProfile = document.getElementById('btn-switch-profile');
    const weightHistoryList = document.getElementById('weight-history-list');

    // Delete Profile Modal
    const deleteModal = document.getElementById('delete-modal');
    const deleteProfileNameEl = document.getElementById('delete-profile-name');
    const btnDeleteCancel = document.getElementById('btn-delete-cancel');
    const btnDeleteConfirm = document.getElementById('btn-delete-confirm');

    // Active State
    let USER_ID = null;
    let USER_NAME = "";
    let USER_AVATAR = "🐉";
    let pendingAuthUserId = null;
    let pendingDeleteProfileId = null;
    let pendingDeleteProfileName = "";

    // Helper to escape HTML tags to prevent XSS
    function escapeHTML(text) {
        if (!text) return "";
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // A simple function to render markdown-like text safely
    function formatMessage(text) {
        let safeText = escapeHTML(text);
        // Basic markdown parsing for bold and line breaks
        let html = safeText
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');
        return html;
    }

    function appendUserMessage(text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message user-message';
        msgDiv.innerHTML = `<div class="message-content">${escapeHTML(text)}</div>`;
        chatContainer.appendChild(msgDiv);
        scrollToBottom();
    }

    function appendSystemMessage(text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message system-message';
        msgDiv.innerHTML = `<div class="message-content">${formatMessage(text)}</div>`;
        chatContainer.appendChild(msgDiv);
        scrollToBottom();
    }

    function showLoading() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message system-message loading-message';
        loadingDiv.id = 'loading-message';
        loadingDiv.innerHTML = `
            <div class="message-content typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <span class="analyzing-text">Analyzing...</span>
            </div>
        `;
        chatContainer.appendChild(loadingDiv);
        scrollToBottom();
    }

    function hideLoading() {
        const loadingDiv = document.getElementById('loading-message');
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Navigation state manager
    function showScreen(screen) {
        // Hide all screens
        welcomeScreen.style.display = 'none';
        selectorScreen.style.display = 'none';
        creationScreen.style.display = 'none';
        chatContainerWrap.style.display = 'none';
        authModal.style.display = 'none';
        
        // Show selected screen
        if (screen === 'welcome') welcomeScreen.style.display = 'flex';
        else if (screen === 'selector') selectorScreen.style.display = 'flex';
        else if (screen === 'creation') creationScreen.style.display = 'flex';
        else if (screen === 'chat') {
            chatContainerWrap.style.display = 'flex';
            setTimeout(() => {
                if (typeof leafletMap !== 'undefined' && leafletMap) {
                    leafletMap.invalidateSize();
                }
            }, 250);
        }
    }

    // Load available profiles
    async function loadProfiles() {
        try {
            const response = await fetch(`${API_BASE}/users/profiles`);
            if (!response.ok) throw new Error("Failed to load profiles");
            const profiles = await response.json();
            
            if (profiles.length === 0) {
                showScreen('welcome');
            } else {
                renderProfilesGrid(profiles);
                showScreen('selector');
            }
        } catch (err) {
            console.error(err);
            // Fallback to onboarding if API fails
            showScreen('welcome');
        }
    }

    // Render Profiles Grid
    function renderProfilesGrid(profiles) {
        profilesGrid.innerHTML = "";
        
        profiles.forEach(p => {
            const card = document.createElement('div');
            card.className = 'profile-card glass-card';
            card.style.position = 'relative';
            
            const avatarEmoji = p.avatar || "🐉";
            const lastLoginText = p.last_login 
                ? `Last seen: ${new Date(p.last_login).toLocaleDateString()}` 
                : "New profile";
                
            card.innerHTML = `
                <div class="profile-avatar">${avatarEmoji}</div>
                <h3>${escapeHTML(p.full_name || p.username)}</h3>
                <p class="profile-meta">${lastLoginText}</p>
                <button class="btn-delete-profile" title="Delete Profile">🗑</button>
            `;
            
            // Click on the card body opens auth modal
            card.addEventListener('click', (e) => {
                // Don't open auth if the delete button was clicked
                if (e.target.closest('.btn-delete-profile')) return;
                openAuthModal(p.id, p.full_name || p.username);
            });

            // Delete button opens delete confirmation modal
            const deleteBtn = card.querySelector('.btn-delete-profile');
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                pendingDeleteProfileId = p.id;
                pendingDeleteProfileName = p.full_name || p.username;
                deleteProfileNameEl.textContent = pendingDeleteProfileName;
                deleteModal.style.display = 'flex';
            });
            
            profilesGrid.appendChild(card);
        });
        
        // Create profile card button
        const addCard = document.createElement('div');
        addCard.className = 'profile-card add-profile-card glass-card';
        addCard.innerHTML = `
            <div class="profile-avatar">+</div>
            <h3>Create Profile</h3>
            <p class="profile-meta">Add new health tracking profile</p>
        `;
        addCard.addEventListener('click', () => {
            showScreen('creation');
        });
        
        profilesGrid.appendChild(addCard);
    }

    // Auth password PIN modal
    function openAuthModal(userId, name) {
        pendingAuthUserId = userId;
        authProfileName.textContent = name;
        authPinInput.value = "";
        authRememberCheck.checked = false;
        authModal.style.display = 'flex';
        authPinInput.focus();
    }

    // Start Session (Chat login success)
    async function startSession(userId, name, avatar) {
        USER_ID = userId;
        USER_NAME = name;
        USER_AVATAR = avatar || "🐉";
        
        document.getElementById('active-profile-name').textContent = USER_NAME;
        document.getElementById('active-profile-avatar').textContent = USER_AVATAR;
        
        // Clear chat area
        chatContainer.innerHTML = `
            <div class="message system-message">
                <div class="message-content">Welcome back, **${escapeHTML(USER_NAME)}**! I'm Toothless, your AI health companion. How are you feeling today?</div>
            </div>
        `;
        
        showScreen('chat');
        
        // Load recent conversations if any
        try {
            const res = await fetch(`${API_BASE}/toothless/conversations/${USER_ID}`);
            if (res.ok) {
                const conversations = await res.json();
                if (conversations.length > 0) {
                    const messages = conversations[0].messages;
                    if (messages && messages.length > 0) {
                        chatContainer.innerHTML = ""; // Clear welcome
                        messages.forEach(msg => {
                            if (msg.role === 'user') {
                                appendUserMessage(msg.content);
                            } else {
                                appendSystemMessage(msg.content);
                            }
                        });
                    }
                }
            }
        } catch (err) {
            console.error("Could not restore previous chat history:", err);
        }
    }

    // persistent cookie/remember me auto check
    async function checkRememberToken() {
        const storedToken = localStorage.getItem('toothless_remember_token');
        const storedUserId = localStorage.getItem('toothless_user_id');
        
        if (storedToken && storedUserId) {
            try {
                const res = await fetch(`${API_BASE}/users/profiles/remember-me/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: storedUserId, token: storedToken })
                });
                
                if (res.ok) {
                    // Fetch full profile info for name and avatar
                    const pRes = await fetch(`${API_BASE}/users/profiles/${storedUserId}`);
                    if (pRes.ok) {
                        const profile = await pRes.json();
                        startSession(profile.id, profile.full_name || profile.username, profile.avatar);
                        return;
                    }
                }
            } catch (err) {
                console.error("Auto login check failed:", err);
            }
            
            // Clear stale values if token fails
            localStorage.removeItem('toothless_remember_token');
            localStorage.removeItem('toothless_user_id');
        }
        
        // standard flow
        loadProfiles();
    }

    // Button controls
    btnStartCreate.addEventListener('click', () => {
        showScreen('creation');
    });

    btnCreateBack.addEventListener('click', () => {
        loadProfiles();
    });

    // Delete Profile Modal Controls
    btnDeleteCancel.addEventListener('click', () => {
        deleteModal.style.display = 'none';
        pendingDeleteProfileId = null;
        pendingDeleteProfileName = "";
    });

    btnDeleteConfirm.addEventListener('click', async () => {
        if (!pendingDeleteProfileId) return;

        try {
            const res = await fetch(`${API_BASE}/users/profiles/${pendingDeleteProfileId}`, {
                method: 'DELETE'
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || "Failed to delete profile");
            }

            // If the deleted profile is the currently active session, terminate it
            if (USER_ID && USER_ID === pendingDeleteProfileId) {
                localStorage.removeItem('toothless_remember_token');
                localStorage.removeItem('toothless_user_id');
                USER_ID = null;
                USER_NAME = "";
            }

            // Also clear remember-me if the deleted profile matches stored ID
            const storedUserId = localStorage.getItem('toothless_user_id');
            if (storedUserId === pendingDeleteProfileId) {
                localStorage.removeItem('toothless_remember_token');
                localStorage.removeItem('toothless_user_id');
            }

            deleteModal.style.display = 'none';
            pendingDeleteProfileId = null;
            pendingDeleteProfileName = "";

            // Refresh the profile list (stays on login screen)
            loadProfiles();
        } catch (err) {
            alert("Delete Failed: " + err.message);
        }
    });

    btnAuthCancel.addEventListener('click', () => {
        authModal.style.display = 'none';
        pendingAuthUserId = null;
    });

    // Submitting Onboarding Profile Form
    document.getElementById('profile-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('p-username').value.trim();
        const password = document.getElementById('p-password').value;
        const fullName = document.getElementById('p-fullname').value.trim();
        const dob = document.getElementById('p-dob').value;
        const gender = document.getElementById('p-gender').value;
        const height = parseFloat(document.getElementById('p-height').value);
        const weight = parseFloat(document.getElementById('p-weight').value);
        const blood = document.getElementById('p-blood').value;
        const avatar = document.querySelector('input[name="avatar"]:checked').value;
        
        const ecName = document.getElementById('p-ec-name').value.trim();
        const ecRel = document.getElementById('p-ec-rel').value.trim();
        const ecPhone = document.getElementById('p-ec-phone').value.trim();
        
        const occupation = document.getElementById('p-occupation').value.trim();
        const smoking = document.getElementById('p-smoking').value;
        const alcohol = document.getElementById('p-alcohol').value;
        const exercise = document.getElementById('p-exercise').value;
        const lang = document.getElementById('p-lang').value.trim();
        
        const allergies = document.getElementById('p-allergies').value.trim();
        const conditions = document.getElementById('p-conditions').value.trim();
        const medications = document.getElementById('p-medications').value.trim();
        
        const payload = {
            username,
            password,
            full_name: fullName,
            date_of_birth: dob,
            gender,
            height,
            weight,
            blood_group: blood,
            avatar,
            emergency_contact_name: ecName || null,
            emergency_contact_relationship: ecRel || null,
            emergency_contact_phone: ecPhone || null,
            occupation: occupation || null,
            smoking_status: smoking || null,
            alcohol_consumption: alcohol || null,
            exercise_frequency: exercise || null,
            preferred_language: lang || null,
            allergies: allergies || null,
            existing_conditions: conditions || null,
            current_medications: medications || null
        };
        
        try {
            const res = await fetch(`${API_BASE}/users/profiles`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || "Failed to create profile");
            }
            
            alert("Profile created successfully!");
            document.getElementById('profile-form').reset();
            loadProfiles();
        } catch (err) {
            alert("Error: " + err.message);
        }
    });

    // Submitting authentication PIN dialog
    authForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const pin = authPinInput.value;
        const userId = pendingAuthUserId;
        const rememberMe = authRememberCheck.checked;
        
        if (!pin || !userId) return;
        
        try {
            const res = await fetch(`${API_BASE}/users/profiles/${userId}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pin })
            });
            
            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || "Invalid login PIN");
            }
            
            // Handle Remember Me device register
            if (rememberMe) {
                const remRes = await fetch(`${API_BASE}/users/profiles/${userId}/remember-me/register`, {
                    method: 'POST'
                });
                if (remRes.ok) {
                    const remData = await remRes.json();
                    localStorage.setItem('toothless_remember_token', remData.token);
                    localStorage.setItem('toothless_user_id', userId);
                }
            }
            
            // Fetch profile detail to extract full name and avatar
            const detailsRes = await fetch(`${API_BASE}/users/profiles/${userId}`);
            if (detailsRes.ok) {
                const profile = await detailsRes.json();
                authModal.style.display = 'none';
                startSession(userId, profile.full_name || profile.username, profile.avatar);
            }
        } catch (err) {
            alert("Login Failed: " + err.message);
        }
    });

    // Logout and switch profiles
    btnSwitchProfile.addEventListener('click', async () => {
        if (!USER_ID) return;
        
        if (confirm("Are you sure you want to log out / switch profile?")) {
            try {
                await fetch(`${API_BASE}/users/profiles/${USER_ID}/logout`, { method: 'POST' });
            } catch (err) {
                console.error("Logout request failed:", err);
            }
            
            // Clear auth session
            localStorage.removeItem('toothless_remember_token');
            localStorage.removeItem('toothless_user_id');
            USER_ID = null;
            USER_NAME = "";
            
            loadProfiles();
        }
    });

    // Open profile settings dialog
    btnOpenSettings.addEventListener('click', async () => {
        if (!USER_ID) return;
        
        try {
            const res = await fetch(`${API_BASE}/users/profiles/${USER_ID}`);
            if (!res.ok) throw new Error("Failed to load profile details");
            
            const profile = await res.json();
            
            // Populate inputs
            document.getElementById('s-weight').value = profile.weight;
            document.getElementById('s-height').value = profile.height;
            document.getElementById('s-ec-name').value = profile.emergency_contact_name || "";
            document.getElementById('s-ec-rel').value = profile.emergency_contact_relationship || "";
            document.getElementById('s-ec-phone').value = profile.emergency_contact_phone || "";
            
            document.getElementById('s-occupation').value = profile.occupation || "";
            document.getElementById('s-smoking').value = profile.smoking_status || "No";
            document.getElementById('s-alcohol').value = profile.alcohol_consumption || "Non-drinker";
            document.getElementById('s-exercise').value = profile.exercise_frequency || "Rare";
            document.getElementById('s-lang').value = profile.preferred_language || "";
            
            document.getElementById('s-medications').value = profile.medications;
            document.getElementById('s-conditions').value = profile.conditions;
            document.getElementById('s-allergies').value = profile.allergies;
            
            // Render weight history list
            weightHistoryList.innerHTML = "";
            if (profile.weight_history && profile.weight_history.length > 0) {
                // Sort by recorded date descending
                profile.weight_history.sort((a, b) => new Date(b.recorded_at) - new Date(a.recorded_at));
                
                profile.weight_history.forEach(log => {
                    const dateStr = new Date(log.recorded_at).toLocaleDateString() + " " + new Date(log.recorded_at).toLocaleTimeString();
                    const li = document.createElement('div');
                    li.className = 'history-item';
                    li.innerHTML = `
                        <span class="history-weight">${log.weight} kg</span>
                        <span class="history-date">${dateStr}</span>
                    `;
                    weightHistoryList.appendChild(li);
                });
            } else {
                weightHistoryList.innerHTML = `<div class="history-empty">No weight modifications logged yet.</div>`;
            }
            
            settingsModal.style.display = 'flex';
        } catch (err) {
            alert("Error: " + err.message);
        }
    });

    // Close settings dialog
    btnSettingsClose.addEventListener('click', () => {
        settingsModal.style.display = 'none';
    });

    // Submitting settings update form
    settingsForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const weight = parseFloat(document.getElementById('s-weight').value);
        const height = parseFloat(document.getElementById('s-height').value);
        const ecName = document.getElementById('s-ec-name').value.trim();
        const ecRel = document.getElementById('s-ec-rel').value.trim();
        const ecPhone = document.getElementById('s-ec-phone').value.trim();
        
        const occupation = document.getElementById('s-occupation').value.trim();
        const smoking = document.getElementById('s-smoking').value;
        const alcohol = document.getElementById('s-alcohol').value;
        const exercise = document.getElementById('s-exercise').value;
        const lang = document.getElementById('s-lang').value.trim();
        
        const medications = document.getElementById('s-medications').value.trim();
        const conditions = document.getElementById('s-conditions').value.trim();
        const allergies = document.getElementById('s-allergies').value.trim();
        
        const payload = {
            weight,
            height,
            emergency_contact_name: ecName || null,
            emergency_contact_relationship: ecRel || null,
            emergency_contact_phone: ecPhone || null,
            occupation: occupation || null,
            smoking_status: smoking || null,
            alcohol_consumption: alcohol || null,
            exercise_frequency: exercise || null,
            preferred_language: lang || null,
            medications: medications || "None reported",
            conditions: conditions || "None reported",
            allergies: allergies || "None reported"
        };
        
        try {
            const res = await fetch(`${API_BASE}/users/profiles/${USER_ID}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || "Failed to update profile settings");
            }
            
            alert("Settings updated successfully!");
            settingsModal.style.display = 'none';
        } catch (err) {
            alert("Update Failed: " + err.message);
        }
    });

    // Send AI Chat Message logic
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const message = chatInput.value.trim();
        if (!message) return;

        // Clear input and append message
        chatInput.value = '';
        appendUserMessage(message);

        // Set loading state
        chatInput.disabled = true;
        sendBtn.disabled = true;
        showLoading();

        try {
            // Send the request to /toothless/chat API
            const payload = {
                user_id: USER_ID,
                message: message,
                context: null
            };

            const response = await fetch(`${API_BASE}/toothless/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            hideLoading();

            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error("Active user session not found. Please log in again.");
                }
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to get response");
            }

            const data = await response.json();
            
            // Format and display response
            let assessmentText = data.response || "No assessment generated.";
            appendSystemMessage(assessmentText);

        } catch (error) {
            hideLoading();
            appendSystemMessage("⚠️ Error: " + error.message);
            console.error("API Error:", error);
        } finally {
            // Reset state
            chatInput.disabled = false;
            sendBtn.disabled = false;
            chatInput.focus();
        }
    });

    // ==================== LIVE GPS, MEDICAL MAP & SOS EMERGENCY FEATURE ====================

    // State Variables
    let userLat = null;
    let userLon = null;
    let userAccuracy = null;
    let userAddress = "";
    let watchId = null;
    let lastFetchLat = null;
    let lastFetchLon = null;

    let isSOSActive = false;
    let selectedFacility = null;
    let currentFilter = "all";
    let nearbyFacilitiesList = [];
    let emergencyPhone = "112";

    // Leaflet Objects
    let leafletMap = null;
    let userMarker = null;
    let facilityMarkers = [];
    let routePolyline = null;

    // DOM Elements for Medical Panel & SOS
    const btnActivateSosTop = document.getElementById('btn-activate-sos-top');
    const btnActivateSosSide = document.getElementById('btn-activate-sos-side');
    const sosModal = document.getElementById('sos-modal');
    const btnSosCancel = document.getElementById('btn-sos-cancel');
    const btnSosConfirm = document.getElementById('btn-sos-confirm');
    const sosActiveBanner = document.getElementById('sos-active-banner');
    const btnDeactivateSos = document.getElementById('btn-deactivate-sos');
    const btnCallEmergency = document.getElementById('btn-call-emergency');

    const liveLatVal = document.getElementById('live-lat-val');
    const liveLonVal = document.getElementById('live-lon-val');
    const liveAccVal = document.getElementById('live-acc-val');
    const liveAddressVal = document.getElementById('live-address-val');
    const addressWrap = document.getElementById('address-wrap');

    const locationErrorBox = document.getElementById('location-error-box');
    const locationErrorText = document.getElementById('location-error-text');
    const btnRetryLocation = document.getElementById('btn-retry-location');
    const btnRefreshLocation = document.getElementById('btn-refresh-location');

    const sosModalLat = document.getElementById('sos-modal-lat');
    const sosModalLon = document.getElementById('sos-modal-lon');
    const sosModalAcc = document.getElementById('sos-modal-acc');
    const sosModalAddress = document.getElementById('sos-modal-address');

    const facilitiesListEl = document.getElementById('facilities-list');
    const selectedFacilityCard = document.getElementById('selected-facility-card');
    const selFacName = document.getElementById('sel-fac-name');
    const selFacType = document.getElementById('sel-fac-type');
    const selFacAddress = document.getElementById('sel-fac-address');
    const selFacDist = document.getElementById('sel-fac-dist');
    const selFacEta = document.getElementById('sel-fac-eta');
    const selFacStatus = document.getElementById('sel-fac-status');
    const btnGetDirections = document.getElementById('btn-get-directions');
    const btnOpenNav = document.getElementById('btn-open-nav');

    const routeInfoBanner = document.getElementById('route-info-banner');
    const routeDistText = document.getElementById('route-dist-text');
    const routeEtaText = document.getElementById('route-eta-text');
    const btnClearRoute = document.getElementById('btn-clear-route');

    const mapLoadingOverlay = document.getElementById('map-loading-overlay');

    // Fetch Backend Runtime Configuration
    async function fetchAppConfig() {
        try {
            const res = await fetch(`${API_BASE}/api/config`);
            if (res.ok) {
                const configData = await res.json();
                if (configData.emergency_phone_default) {
                    emergencyPhone = configData.emergency_phone_default;
                    document.getElementById('emergency-phone-num').textContent = emergencyPhone;
                    btnCallEmergency.setAttribute('href', `tel:${emergencyPhone}`);
                }
            }
        } catch (err) {
            console.warn("Could not load backend config, using defaults:", err);
        }
    }

    // 1. Request Location Permission & Live GPS
    function requestLocation(triggerSOSModalAfter = false) {
        if (!navigator.geolocation) {
            showLocationError("Geolocation is not supported by your browser.", triggerSOSModalAfter);
            return;
        }

        liveLatVal.textContent = "Detecting...";
        liveLonVal.textContent = "Detecting...";
        liveAccVal.textContent = "± -- meters";
        if (locationErrorBox) locationErrorBox.style.display = 'none';

        navigator.geolocation.getCurrentPosition(
            (pos) => {
                onLocationSuccess(pos, triggerSOSModalAfter);
            },
            (err) => {
                onLocationError(err, triggerSOSModalAfter);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    }

    // On Location Success Callback
    function onLocationSuccess(pos, triggerSOSModalAfter = false) {
        userLat = pos.coords.latitude;
        userLon = pos.coords.longitude;
        userAccuracy = Math.round(pos.coords.accuracy);

        // Update DOM Displays
        liveLatVal.textContent = userLat.toFixed(6);
        liveLonVal.textContent = userLon.toFixed(6);
        liveAccVal.textContent = `± ${userAccuracy} meters`;
        
        if (sosModalLat) sosModalLat.textContent = userLat.toFixed(6);
        if (sosModalLon) sosModalLon.textContent = userLon.toFixed(6);
        if (sosModalAcc) sosModalAcc.textContent = `± ${userAccuracy} meters`;

        if (locationErrorBox) locationErrorBox.style.display = 'none';

        // Reverse Geocoding
        reverseGeocode(userLat, userLon);

        // Initialize / Update Leaflet Map
        initOrUpdateMap(userLat, userLon);

        // Start Continuous Movement Tracking
        startWatchPosition();

        // Check if movement warrants fetching nearby facilities (> 50m movement or initial load)
        if (!lastFetchLat || calculateHaversineDistance(lastFetchLat, lastFetchLon, userLat, userLon) > 0.05) {
            lastFetchLat = userLat;
            lastFetchLon = userLon;
            fetchNearbyFacilities(userLat, userLon, currentFilter);
        }

        // Open SOS Modal if requested
        if (triggerSOSModalAfter) {
            openSOSModal();
        }
    }

    // On Location Error Callback
    function onLocationError(err, triggerSOSModalAfter = false) {
        let msg = "Unable to determine your current location. Please try again.";
        
        if (err.code === err.PERMISSION_DENIED) {
            msg = "Location access was denied. Please allow location access in your browser settings to use live emergency location features.";
        } else if (err.code === err.POSITION_UNAVAILABLE) {
            msg = "Location services unavailable. Please check your device GPS/location settings and try again.";
        } else if (err.code === err.TIMEOUT) {
            msg = "Location request timed out. Please try again.";
        }

        showLocationError(msg, triggerSOSModalAfter);

        // Fallback default coordinates anchor (e.g. 23.5204, 87.3119) so the interactive map and facilities render immediately
        const fallbackLat = 23.5204;
        const fallbackLon = 87.3119;
        initOrUpdateMap(fallbackLat, fallbackLon);
        if (!lastFetchLat) {
            lastFetchLat = fallbackLat;
            lastFetchLon = fallbackLon;
            fetchNearbyFacilities(fallbackLat, fallbackLon, currentFilter);
        }
    }

    function showLocationError(message, isSOS = false) {
        if (locationErrorText) locationErrorText.textContent = message;
        if (locationErrorBox) locationErrorBox.style.display = 'flex';
        liveLatVal.textContent = "Unavailable";
        liveLonVal.textContent = "Unavailable";

        if (isSOS) {
            alert("⚠️ " + message);
        }
    }

    // Continuous watchPosition for live movement
    function startWatchPosition() {
        if (watchId !== null) return; // Already watching

        if (navigator.geolocation) {
            watchId = navigator.geolocation.watchPosition(
                (pos) => {
                    const lat = pos.coords.latitude;
                    const lon = pos.coords.longitude;
                    const acc = Math.round(pos.coords.accuracy);

                    userLat = lat;
                    userLon = lon;
                    userAccuracy = acc;

                    liveLatVal.textContent = lat.toFixed(6);
                    liveLonVal.textContent = lon.toFixed(6);
                    liveAccVal.textContent = `± ${acc} meters`;

                    // Update Leaflet user marker position
                    if (userMarker) {
                        userMarker.setLatLng([lat, lon]);
                    }

                    // Recalculate route if active and movement > 100 meters
                    if (selectedFacility && routePolyline) {
                        getDirections(selectedFacility);
                    }
                },
                (err) => {
                    console.warn("watchPosition warning:", err.message);
                },
                {
                    enableHighAccuracy: true,
                    maximumAge: 10000,
                    timeout: 15000
                }
            );
        }
    }

    // 2. Reverse Geocoding (Nominatim OpenStreetMap)
    async function reverseGeocode(lat, lon) {
        try {
            const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`);
            if (res.ok) {
                const data = await res.json();
                if (data && data.display_name) {
                    const addressParts = data.display_name.split(',');
                    // Take relevant city/locality parts
                    userAddress = addressParts.slice(0, 3).join(',').trim();
                    liveAddressVal.textContent = userAddress;
                    if (addressWrap) addressWrap.style.display = 'flex';
                    if (sosModalAddress) sosModalAddress.textContent = userAddress;
                }
            }
        } catch (e) {
            console.warn("Reverse geocode fetch failed (non-blocking):", e);
        }
    }

    // 3. Leaflet Map Engine Initialization & Marker Rendering
    function initOrUpdateMap(lat, lon) {
        if (typeof L === 'undefined') {
            console.warn("Leaflet CSS/JS library not loaded");
            return;
        }

        const mapContainer = document.getElementById('medical-map');
        if (!mapContainer) return;

        if (!leafletMap) {
            leafletMap = L.map('medical-map', {
                zoomControl: true,
                attributionControl: false
            }).setView([lat, lon], 14);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19
            }).addTo(leafletMap);

            // Create custom pulsating blue dot for user position
            const userIcon = L.divIcon({
                className: 'user-live-marker',
                html: `<div style="background-color: #6366f1; width: 16px; height: 16px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 10px rgba(99,102,241,0.8);"></div>`,
                iconSize: [22, 22],
                iconAnchor: [11, 11]
            });

            userMarker = L.marker([lat, lon], { icon: userIcon }).addTo(leafletMap);
            userMarker.bindPopup("<strong>📍 You are here</strong><br>Current Live GPS Location").openPopup();
        } else {
            leafletMap.setView([lat, lon], leafletMap.getZoom());
            if (userMarker) userMarker.setLatLng([lat, lon]);
        }
    }

    // 4. Fetch Nearby Medical Facilities via Backend Proxy
    async function fetchNearbyFacilities(lat, lon, filter = "all") {
        if (mapLoadingOverlay) mapLoadingOverlay.style.display = 'flex';

        try {
            const res = await fetch(`${API_BASE}/api/nearby-facilities?lat=${lat}&lon=${lon}&facility_type=${filter}`);
            if (mapLoadingOverlay) mapLoadingOverlay.style.display = 'none';

            if (!res.ok) throw new Error("Failed to load nearby facilities");

            const data = await res.json();
            nearbyFacilitiesList = data.facilities || [];

            renderFacilitiesList(nearbyFacilitiesList);
            renderFacilityMarkersOnMap(nearbyFacilitiesList);

            // If SOS is active, auto select the nearest hospital
            if (isSOSActive && nearbyFacilitiesList.length > 0) {
                const emergencyFac = nearbyFacilitiesList.find(f => f.type === 'hospital' || f.is_emergency_ready) || nearbyFacilitiesList[0];
                selectFacility(emergencyFac);
                getDirections(emergencyFac);
            }

        } catch (err) {
            if (mapLoadingOverlay) mapLoadingOverlay.style.display = 'none';
            console.error("Facilities Error:", err);
            facilitiesListEl.innerHTML = `<div class="facility-skeleton">Unable to load nearby facilities. Please retry.</div>`;
        }
    }

    // Render Facilities Cards List in Panel
    function renderFacilitiesList(facilities) {
        facilitiesListEl.innerHTML = "";

        if (facilities.length === 0) {
            facilitiesListEl.innerHTML = `<div class="facility-skeleton">No medical facilities found nearby.</div>`;
            return;
        }

        facilities.forEach(fac => {
            const card = document.createElement('div');
            card.className = `facility-card ${selectedFacility && selectedFacility.id === fac.id ? 'active-selected' : ''}`;
            
            let iconEmoji = "🏥";
            if (fac.type === "pharmacy") iconEmoji = "💊";
            else if (fac.type === "clinic") iconEmoji = "🩺";

            card.innerHTML = `
                <div style="display: flex; align-items: center;">
                    <span class="fac-icon">${iconEmoji}</span>
                    <div class="fac-info">
                        <div class="fac-name">${escapeHTML(fac.name)}</div>
                        <div class="fac-sub">${escapeHTML(fac.address)}</div>
                    </div>
                </div>
                <div class="fac-meta">
                    <div class="fac-dist">${fac.distance_km} km</div>
                    <div class="fac-eta">~${fac.eta_minutes} min</div>
                </div>
            `;

            card.addEventListener('click', () => {
                selectFacility(fac);
            });

            facilitiesListEl.appendChild(card);
        });
    }

    // Render Markers on Leaflet Map
    function renderFacilityMarkersOnMap(facilities) {
        if (!leafletMap) return;

        // Clear existing markers
        facilityMarkers.forEach(m => leafletMap.removeLayer(m));
        facilityMarkers = [];

        facilities.forEach(fac => {
            let emoji = "🏥";
            if (fac.type === "pharmacy") emoji = "💊";
            else if (fac.type === "clinic") emoji = "🩺";

            const facIcon = L.divIcon({
                className: 'fac-map-marker',
                html: `<div style="font-size: 1.4rem; cursor: pointer; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">${emoji}</div>`,
                iconSize: [28, 28],
                iconAnchor: [14, 14]
            });

            const marker = L.marker([fac.latitude, fac.longitude], { icon: facIcon }).addTo(leafletMap);
            marker.bindPopup(`
                <strong>${escapeHTML(fac.name)}</strong><br>
                Type: ${fac.type.toUpperCase()}<br>
                Distance: ${fac.distance_km} km (~${fac.eta_minutes} min)<br>
                <em>${escapeHTML(fac.open_status)}</em>
            `);

            marker.on('click', () => {
                selectFacility(fac);
            });

            facilityMarkers.push(marker);
        });
    }

    // Select Facility Event
    function selectFacility(fac) {
        selectedFacility = fac;

        // Update detail card UI
        selFacName.textContent = fac.name;
        selFacType.textContent = fac.type.toUpperCase();
        selFacAddress.textContent = fac.address;
        selFacDist.textContent = `${fac.distance_km} km`;
        selFacEta.textContent = `~${fac.eta_minutes} min`;
        selFacStatus.textContent = fac.open_status;

        selectedFacilityCard.style.display = 'block';
        selectedFacilityCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        // Highlight selected facility card list item
        renderFacilitiesList(nearbyFacilitiesList);

        // Center map on selected facility
        if (leafletMap) {
            leafletMap.panTo([fac.latitude, fac.longitude]);
        }
    }

    // 5. Get Real Driving Route & Directions via Backend Proxy
    async function getDirections(fac) {
        if (!userLat || !userLon || !fac) return;

        try {
            const url = `${API_BASE}/api/route?start_lat=${userLat}&start_lon=${userLon}&end_lat=${fac.latitude}&end_lon=${fac.longitude}`;
            const res = await fetch(url);

            if (!res.ok) throw new Error("Routing failed");

            const routeData = await res.json();
            const geometry = routeData.geometry;

            if (geometry && geometry.length > 0 && leafletMap) {
                // Remove existing route polyline
                if (routePolyline) leafletMap.removeLayer(routePolyline);

                // Draw real driving polyline
                routePolyline = L.polyline(geometry, {
                    color: '#6366f1',
                    weight: 5,
                    opacity: 0.8,
                    dashArray: isSOSActive ? '8, 8' : null
                }).addTo(leafletMap);

                // Fit map to show full route bounds
                leafletMap.fitBounds(routePolyline.getBounds(), { padding: [30, 30] });

                // Display active route banner
                routeDistText.textContent = `${routeData.distance_km} km`;
                routeEtaText.textContent = `~${routeData.duration_minutes} min`;
                routeInfoBanner.style.display = 'block';
            }
        } catch (err) {
            console.error("Routing error:", err);
            alert("Route directions temporarily unavailable. Opening external navigation option.");
        }
    }

    // Open External Navigation (Google Maps)
    function openExternalNav(fac) {
        if (!userLat || !userLon || !fac) return;
        const navUrl = `https://www.google.com/maps/dir/?api=1&origin=${userLat},${userLon}&destination=${fac.latitude},${fac.longitude}&travelmode=driving`;
        window.open(navUrl, '_blank');
    }

    // Clear Route
    function clearRoute() {
        if (routePolyline && leafletMap) {
            leafletMap.removeLayer(routePolyline);
            routePolyline = null;
        }
        routeInfoBanner.style.display = 'none';
    }

    // Haversine Distance helper for movement threshold check
    function calculateHaversineDistance(lat1, lon1, lat2, lon2) {
        const R = 6371;
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return R * c;
    }

    // 6. SOS Emergency Workflow Events
    function openSOSWorkflow() {
        if (!userLat || !userLon) {
            requestLocation(true);
        } else {
            openSOSModal();
        }
    }

    function openSOSModal() {
        if (sosModalLat) sosModalLat.textContent = userLat ? userLat.toFixed(6) : "Detecting...";
        if (sosModalLon) sosModalLon.textContent = userLon ? userLon.toFixed(6) : "Detecting...";
        if (sosModalAcc) sosModalAcc.textContent = userAccuracy ? `± ${userAccuracy} meters` : "± -- meters";
        if (sosModalAddress) sosModalAddress.textContent = userAddress || "";
        sosModal.style.display = 'flex';
    }

    function closeSOSModal() {
        sosModal.style.display = 'none';
    }

    function confirmSOS() {
        closeSOSModal();
        isSOSActive = true;
        sosActiveBanner.style.display = 'block';

        // Set filter to emergency/hospitals
        currentFilter = "hospital";
        document.querySelectorAll('.filter-chip').forEach(c => {
            c.classList.toggle('active', c.getAttribute('data-filter') === 'hospital');
        });

        // Refresh nearby facilities prioritizing emergency hospitals
        if (userLat && userLon) {
            fetchNearbyFacilities(userLat, userLon, "hospital");
        }
    }

    function deactivateSOS() {
        isSOSActive = false;
        sosActiveBanner.style.display = 'none';
        clearRoute();
    }

    // Event Listeners for SOS & Location Controls
    btnActivateSosTop.addEventListener('click', openSOSWorkflow);
    btnActivateSosSide.addEventListener('click', openSOSWorkflow);
    btnSosCancel.addEventListener('click', closeSOSModal);
    btnSosConfirm.addEventListener('click', confirmSOS);
    btnDeactivateSos.addEventListener('click', deactivateSOS);

    if (btnRefreshLocation) {
        btnRefreshLocation.addEventListener('click', () => requestLocation(false));
    }
    if (btnRetryLocation) {
        btnRetryLocation.addEventListener('click', () => requestLocation(false));
    }

    if (btnGetDirections) {
        btnGetDirections.addEventListener('click', () => {
            if (selectedFacility) getDirections(selectedFacility);
        });
    }

    if (btnOpenNav) {
        btnOpenNav.addEventListener('click', () => {
            if (selectedFacility) openExternalNav(selectedFacility);
        });
    }

    if (btnClearRoute) {
        btnClearRoute.addEventListener('click', clearRoute);
    }

    // Facility Filter Chip Click Events
    document.querySelectorAll('.filter-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            currentFilter = chip.getAttribute('data-filter');

            if (userLat && userLon) {
                fetchNearbyFacilities(userLat, userLon, currentFilter);
            }
        });
    });

    // Automatically trigger GPS & Location initialization when user starts session
    const originalStartSession = startSession;
    startSession = async function(userId, name, avatar) {
        await originalStartSession(userId, name, avatar);
        fetchAppConfig();
        // Request live location automatically on session start
        requestLocation(false);
    };

    // Run persistent remember token check on load & load runtime config
    fetchAppConfig();
    checkRememberToken();
});

