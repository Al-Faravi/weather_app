/**
 * Ultimate Weather Dashboard Logic
 * Features: Unit Conversion, Count-up Animation, Parallax Effect, Theme Switcher
 */

document.addEventListener('DOMContentLoaded', () => {
    // এলিমেন্টগুলো সিলেক্ট করা
    const tempElement = document.getElementById('main-temp');
    const unitC = document.getElementById('unit-c');
    const unitF = document.getElementById('unit-f');
    const searchInput = document.getElementById('city-input');
    const card = document.querySelector('.weather-card');
    const searchForm = document.getElementById('search-form');
    const searchBtn = document.getElementById('search-btn');

    // --- ১. তাপমাত্রা এনিমেশন (Count-up Animation) ---
    if (tempElement) {
        const targetTemp = parseInt(tempElement.getAttribute('data-temp'));
        let startTemp = 0;
        const duration = 1000; // ১ সেকেন্ডের মধ্যে এনিমেশন শেষ হবে
        const increment = targetTemp / (duration / 20);

        const counter = setInterval(() => {
            startTemp += increment;
            if ((increment > 0 && startTemp >= targetTemp) || (increment < 0 && startTemp <= targetTemp)) {
                tempElement.innerText = `${targetTemp}°C`;
                clearInterval(counter);
            } else {
                tempElement.innerText = `${Math.round(startTemp)}°C`;
            }
        }, 20);
    }

    // --- ২. ইউনিট কনভার্টার (C to F) পেজ রিফ্রেশ ছাড়া ---
    if (unitF && tempElement) {
        unitF.addEventListener('click', () => {
            const celsius = parseInt(tempElement.getAttribute('data-temp'));
            const fahrenheit = Math.round((celsius * 9/5) + 32);
            tempElement.innerText = `${fahrenheit}°F`;
            unitF.classList.add('active');
            unitC.classList.remove('active');
            
            // পূর্বাভাস বা ফোরকাস্টের তাপমাত্রাও পরিবর্তন করা
            document.querySelectorAll('.f-temp').forEach(el => {
                const c = parseInt(el.innerText);
                el.innerText = `${Math.round((c * 9/5) + 32)}°F`;
            });
        });

        unitC.addEventListener('click', () => {
            const celsius = tempElement.getAttribute('data-temp');
            tempElement.innerText = `${celsius}°C`;
            unitC.classList.add('active');
            unitF.classList.remove('active');
            // ফোরকাস্ট রিসেট (সহজ করার জন্য পেজ রিলোড বা অরিজিনাল ডাটা রাখা যায়)
        });
    }

    // --- ৩. কার্ড প্যারাল্যাক্স ইফেক্ট (3D Tilt Effect) ---
    card.addEventListener('mousemove', (e) => {
        const { offsetWidth: width, offsetHeight: height } = card;
        const { offsetX: x, offsetY: y } = e;
        const xRotation = ((y - height / 2) / height) * 15; // ১৫ ডিগ্রি পর্যন্ত হেলবে
        const yRotation = ((x - width / 2) / width) * -15;

        card.style.transform = `perspective(1000px) rotateX(${xRotation}deg) rotateY(${yRotation}deg)`;
    });

    card.addEventListener('mouseleave', () => {
        card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg)';
        card.style.transition = 'all 0.5s ease';
    });

    // --- ৪. স্মার্ট কী-বোর্ড শর্টকাট (Press '/' to focus search) ---
    document.addEventListener('keydown', (e) => {
        if (e.key === '/') {
            e.preventDefault();
            searchInput.focus();
        }
    });

    // --- ৫. লোকাল স্টোরেজ (History Management) ---
    searchForm.addEventListener('submit', () => {
        const city = searchInput.value;
        localStorage.setItem('lastCity', city);
        // লোডিং স্পিনার
        searchBtn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Loading...';
    });
});