/**
 * Weather Dashboard Pro - Logic
 * Features: 
 * - Geolocation (Auto-location)
 * - Persistent Search History (LocalStorage)
 * - Accurate Unit Conversion (C/F)
 * - Smooth Count-up Animation
 * - Keyboard Shortcuts ('/')
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- ১. এলিমেন্ট সিলেকশন ---
    const tempElement = document.getElementById('main-temp');
    const unitC = document.getElementById('unit-c');
    const unitF = document.getElementById('unit-f');
    const searchInput = document.getElementById('city-input');
    const searchForm = document.getElementById('search-form');
    const searchBtn = document.getElementById('search-btn');
    const geoBtn = document.getElementById('geo-btn');
    const historyContainer = document.getElementById('history-container');
    const forecastTemps = document.querySelectorAll('.f-temp');

    // --- ২. সার্চ হিস্ট্রি ম্যানেজমেন্ট ---
    
    // হিস্ট্রি রেন্ডার করা (UI তে দেখানো)
    const renderHistory = () => {
        const history = JSON.parse(localStorage.getItem('weatherHistory') || '[]');
        if (!historyContainer) return;
        
        historyContainer.innerHTML = '';
        history.forEach(city => {
            const tag = document.createElement('span');
            tag.className = 'history-tag';
            tag.innerText = city;
            tag.title = `Search ${city}`;
            
            // ট্যাগ ক্লিক করলে সরাসরি সার্চ হবে
            tag.onclick = () => {
                searchInput.value = city;
                searchForm.dispatchEvent(new Event('submit')); // ফর্ম সাবমিট ট্রিগার
                searchForm.submit();
            };
            historyContainer.appendChild(tag);
        });
    };

    // হিস্ট্রিতে শহর সেভ করা
    const saveToHistory = (city) => {
        if (!city) return;
        let history = JSON.parse(localStorage.getItem('weatherHistory') || '[]');
        
        // নাম ফরম্যাট করা (যেমন: dhaka -> Dhaka)
        const formattedCity = city.charAt(0).toUpperCase() + city.slice(1).toLowerCase();
        
        // ডুপ্লিকেট রিমুভ করে শুরুতে নতুন শহর যোগ করা
        history = history.filter(item => item !== formattedCity);
        history.unshift(formattedCity);
        
        // সর্বোচ্চ ৫টি শহর রাখা
        if (history.length > 5) history.pop();
        
        localStorage.setItem('weatherHistory', JSON.stringify(history));
        renderHistory();
    };

    // --- ৩. অটো-লোকেশন (Geolocation API) ---
    if (geoBtn) {
        geoBtn.addEventListener('click', () => {
            if (navigator.geolocation) {
                geoBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>'; // লোডিং আইকন
                
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const { latitude, longitude } = position.coords;
                        // URL প্যারামিটার দিয়ে Flask এ পাঠানো
                        window.location.href = `/?lat=${latitude}&lon=${longitude}`;
                    },
                    (error) => {
                        console.error(error);
                        alert("লোকেশন পাওয়া যায়নি। অনুগ্রহ করে শহরের নাম টাইপ করুন।");
                        geoBtn.innerHTML = '<i class="fas fa-crosshairs"></i>';
                    }
                );
            } else {
                alert("আপনার ব্রাউজার জিও-লোকেশন সাপোর্ট করে না।");
            }
        });
    }

    // --- ৪. তাপমাত্রা কাউন্ট-আপ এনিমেশন ---
    if (tempElement) {
        const targetTemp = parseInt(tempElement.getAttribute('data-temp'));
        
        const animateValue = (obj, start, end, duration) => {
            let startTimestamp = null;
            const step = (timestamp) => {
                if (!startTimestamp) startTimestamp = timestamp;
                const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                obj.innerHTML = Math.floor(progress * (end - start) + start) + "°C";
                if (progress < 1) {
                    window.requestAnimationFrame(step);
                }
            };
            window.requestAnimationFrame(step);
        };
        
        animateValue(tempElement, 0, targetTemp, 1000);
    }

    // --- ৫. ইউনিট কনভার্টার (নির্ভুল লজিক) ---
    if (unitF && unitC && tempElement) {
        // ফোরকাস্টের অরিজিনাল ভ্যালু অ্যাট্রিবিউটে সেভ করা
        forecastTemps.forEach(el => {
            el.setAttribute('data-orig-c', el.innerText.replace('°C', ''));
        });

        unitF.addEventListener('click', () => {
            if (unitF.classList.contains('active')) return;

            const c = parseInt(tempElement.getAttribute('data-temp'));
            tempElement.innerText = `${Math.round((c * 9/5) + 32)}°F`;

            forecastTemps.forEach(el => {
                const fc = parseInt(el.getAttribute('data-orig-c'));
                el.innerText = `${Math.round((fc * 9/5) + 32)}°F`;
            });

            unitF.classList.add('active');
            unitC.classList.remove('active');
        });

        unitC.addEventListener('click', () => {
            if (unitC.classList.contains('active')) return;

            tempElement.innerText = `${tempElement.getAttribute('data-temp')}°C`;

            forecastTemps.forEach(el => {
                el.innerText = `${el.getAttribute('data-orig-c')}°C`;
            });

            unitC.classList.add('active');
            unitF.classList.remove('active');
        });
    }

    // --- ৬. কী-বোর্ড শর্টকাট ('/') ---
    document.addEventListener('keydown', (e) => {
        if (e.key === '/' && document.activeElement !== searchInput) {
            e.preventDefault();
            searchInput.focus();
        }
    });

    // --- ৭. ফর্ম সাবমিশন লজিক ---
    if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
            const cityValue = searchInput.value.trim();
            if (cityValue) {
                saveToHistory(cityValue);
                searchBtn.disabled = true;
                searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            }
        });
    }

    // পেজ লোড হওয়ার সময় হিস্ট্রি দেখানো
    renderHistory();
});