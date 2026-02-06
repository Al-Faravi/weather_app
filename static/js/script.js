document.addEventListener('DOMContentLoaded', () => {

    // --- ১. রিয়েল-টাইম ঘড়ি (Universal Support) ---
    function updateClock() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        
        // নতুন ডিজাইনের জন্য (Smart Dashboard)
        const clockElem = document.getElementById('clock');
        if (clockElem) {
            clockElem.innerText = timeString;
        }
    }
    setInterval(updateClock, 1000);
    updateClock();


    // --- ২. চার্ট কনফিগারেশন (Chart.js) ---
    const ctx = document.getElementById('hourlyChart');
    if (ctx && window.hourlyLabels && window.hourlyLabels.length > 0) {
        
        // গ্রাফের নিচে সুন্দর গ্রাডিয়েন্ট ইফেক্ট
        let gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(0, 210, 255, 0.4)'); // উপরে উজ্জ্বল নীল
        gradient.addColorStop(1, 'rgba(0, 210, 255, 0)');   // নিচে ফেইড আউট

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: window.hourlyLabels,
                datasets: [{
                    label: 'Temp (°C)',
                    data: window.hourlyData,
                    borderColor: '#00d2ff',       // লাইন কালার (Neon Blue)
                    backgroundColor: gradient,    // ফিল কালার
                    borderWidth: 3,
                    pointBackgroundColor: '#fff',
                    pointBorderColor: '#00d2ff',
                    pointRadius: 4,
                    pointHoverRadius: 7,
                    fill: true,
                    tension: 0.4 // স্মুথ কার্ভ
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(20, 20, 35, 0.9)',
                        titleColor: '#fff',
                        bodyColor: '#00d2ff',
                        padding: 10,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                return context.parsed.y + '°C';
                            }
                        }
                    }
                },
                scales: {
                    x: { 
                        ticks: { color: 'rgba(255,255,255,0.7)', font: { family: "'Outfit', sans-serif", size: 11 } }, 
                        grid: { display: false } 
                    },
                    y: { 
                        display: false, // ক্লিন লুকের জন্য Y-axis লুকানো
                        grid: { display: false } 
                    }
                }
            }
        });
    }


    // --- ৩. অটো-কমপ্লিট সার্চ (Teleport API) ---
    const searchInput = document.getElementById('city-input');
    const suggestionsList = document.getElementById('suggestions-list');
    let debounceTimer;

    if (searchInput && suggestionsList) {
        
        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            const query = searchInput.value.trim();
            
            if (query.length < 3) {
                suggestionsList.style.display = 'none';
                return;
            }

            debounceTimer = setTimeout(async () => {
                try {
                    const response = await fetch(`https://api.teleport.org/api/cities/?search=${query}`);
                    const data = await response.json();
                    
                    if (data._embedded && data._embedded['city:search-results'].length > 0) {
                        const cities = data._embedded['city:search-results'];
                        
                        suggestionsList.innerHTML = '';
                        suggestionsList.style.display = 'block';

                        cities.slice(0, 5).forEach(city => {
                            const li = document.createElement('li');
                            li.innerHTML = `<i class="fas fa-map-marker-alt" style="margin-right:8px; opacity:0.6;"></i> ${city.matching_full_name}`;
                            
                            li.onclick = () => {
                                searchInput.value = city.matching_full_name.split(',')[0];
                                suggestionsList.style.display = 'none';
                            };
                            suggestionsList.appendChild(li);
                        });
                    } else {
                        suggestionsList.style.display = 'none';
                    }
                } catch (err) {
                    console.error("Suggestion error:", err);
                }
            }, 300);
        });

        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-box')) {
                suggestionsList.style.display = 'none';
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === '/' && document.activeElement !== searchInput) {
                e.preventDefault();
                searchInput.focus();
            }
        });
    }

    // --- ৪. Leaflet Live Weather Map ---
    const API_KEY = "b140d4764e7e30ec785c37515da8ea5d"; // OpenWeatherMap Key
    const mapContainer = document.getElementById('weatherMap');

    // চেক করা হচ্ছে ম্যাপ কন্টেইনার এবং কো-অর্ডিনেট আছে কি না
    if (mapContainer && window.weatherLat != null && window.weatherLon != null) {
        
        // ১. ম্যাপ তৈরি এবং সেন্টার সেট করা [Lat, Lon]
        const map = L.map('weatherMap', {
            center: [window.weatherLat, window.weatherLon],
            zoom: 10,
            zoomControl: false,
            attributionControl: false
        });

        // ২. ডার্ক বেস ম্যাপ লেয়ার
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            maxZoom: 19,
            subdomains: 'abcd'
        }).addTo(map);

        // ৩. মেঘের লেয়ার
        L.tileLayer(`https://tile.openweathermap.org/map/clouds_new/{z}/{x}/{y}.png?appid=${API_KEY}`, {
            opacity: 0.8
        }).addTo(map);

        // ৪. বৃষ্টির লেয়ার
        L.tileLayer(`https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid=${API_KEY}`, {
            opacity: 0.6
        }).addTo(map);

        // ৫. লোকেশন মার্কার
        L.marker([window.weatherLat, window.weatherLon])
            .addTo(map)
            .bindPopup(`<b style="color:black;">Current Location</b>`)
            .openPopup();
    }
});


// --- ৫. AI Chatbot Logic (NEW) ---

function toggleChat() {
    const chatBox = document.getElementById('chatBox');
    if (chatBox.style.display === 'flex') {
        chatBox.style.display = 'none';
    } else {
        chatBox.style.display = 'flex';
        // চ্যাটবক্স ওপেন হলে ফোকাস ইনপুটে নাও
        setTimeout(() => document.getElementById('userQuestion').focus(), 100);
    }
}

function handleEnter(e) {
    if (e.key === 'Enter') askAI();
}

async function askAI() {
    const inputField = document.getElementById('userQuestion');
    const question = inputField.value.trim();
    const chatBody = document.getElementById('chatBody');

    if (!question) return;

    // 1. ব্যবহারকারীর প্রশ্ন শো করা
    chatBody.innerHTML += `<div class="user-msg">${question}</div>`;
    inputField.value = '';
    chatBody.scrollTop = chatBody.scrollHeight;

    // 2. লোডিং মেসেজ দেখানো
    const loadingId = 'loading-' + Date.now();
    chatBody.innerHTML += `<div class="bot-msg" id="${loadingId}">টাইপ করছি... ✍️</div>`;
    chatBody.scrollTop = chatBody.scrollHeight;

    try {
        // 3. ব্যাকএন্ডে রিকোয়েস্ট পাঠানো
        const response = await fetch('/ask_ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: question,
                context: window.weatherContext // HTML থেকে আসা আবহাওয়ার ডাটা
            })
        });

        const data = await response.json();
        
        // 4. উত্তর আপডেট করা
        const loadingElem = document.getElementById(loadingId);
        if (loadingElem) loadingElem.remove();
        
        chatBody.innerHTML += `<div class="bot-msg">${data.answer}</div>`;

    } catch (error) {
        console.error("AI Error:", error);
        const loadingElem = document.getElementById(loadingId);
        if (loadingElem) {
            loadingElem.innerHTML = "দুঃখিত, সার্ভারে সমস্যা হচ্ছে। আবার চেষ্টা করুন। ⚠️";
        }
    }
    chatBody.scrollTop = chatBody.scrollHeight;
}