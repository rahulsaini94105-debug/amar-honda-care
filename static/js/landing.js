/* ==========================================================================
   AMAR HONDA CARE - PUBLIC LANDING PAGE INTERACTIVE & 3D ANIMATION SCRIPT
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Navbar Scroll Effect
    const navbar = document.querySelector('.landing-navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 40) {
            navbar?.classList.add('scrolled');
        } else {
            navbar?.classList.remove('scrolled');
        }
    });

    // 2. Three.js 3D Background Canvas Animation
    initHero3DCanvas();

    // 3. 3D Card Tilt Physics Effect
    init3DCardTilt();

    // 4. Interactive Service Calculator
    const modelSelect = document.getElementById('calcBikeModel');
    const serviceTypeSelect = document.getElementById('calcServiceType');
    const addonOil = document.getElementById('addonOil');
    const addonPolish = document.getElementById('addonPolish');
    const addonBreakdown = document.getElementById('addonBreakdown');
    
    const displayBasePrice = document.getElementById('calcBasePrice');
    const displayOilPrice = document.getElementById('calcOilPrice');
    const displayPolishPrice = document.getElementById('calcPolishPrice');
    const displayGrandTotal = document.getElementById('calcGrandTotal');

    const servicePricing = {
        'general': 450,
        'full_tune': 750,
        'engine_overhaul': 2200,
        'brake_clutch': 350,
        'wash_detail': 250
    };

    const modelMultiplier = {
        'activa': 1.0,
        'dio': 1.0,
        'shine': 1.1,
        'sp125': 1.1,
        'unicorn': 1.25,
        'hornet': 1.35,
        'cb350': 1.6
    };

    function calculateEstimate() {
        if (!serviceTypeSelect || !displayGrandTotal) return;

        const model = modelSelect ? modelSelect.value : 'activa';
        const service = serviceTypeSelect.value;
        const mult = modelMultiplier[model] || 1.0;
        
        let base = (servicePricing[service] || 450) * mult;
        let oilCost = addonOil && addonOil.checked ? 380 : 0;
        let polishCost = addonPolish && addonPolish.checked ? 200 : 0;
        let breakdownCost = addonBreakdown && addonBreakdown.checked ? 150 : 0;

        let total = base + oilCost + polishCost + breakdownCost;

        if (displayBasePrice) displayBasePrice.innerText = `₹${Math.round(base)}`;
        if (displayOilPrice) displayOilPrice.innerText = `₹${oilCost}`;
        if (displayPolishPrice) displayPolishPrice.innerText = `₹${polishCost}`;
        displayGrandTotal.innerText = `₹${Math.round(total)}`;
    }

    [modelSelect, serviceTypeSelect, addonOil, addonPolish, addonBreakdown].forEach(el => {
        el?.addEventListener('change', calculateEstimate);
    });

    calculateEstimate();

    // 5. Live Service Status Checker
    const statusForm = document.getElementById('statusCheckForm');
    const statusResult = document.getElementById('statusResultBox');

    statusForm?.addEventListener('submit', (e) => {
        e.preventDefault();
        const regInput = document.getElementById('statusRegInput')?.value.trim().toUpperCase();
        if (!regInput) return;

        statusResult.innerHTML = `
            <div class="text-center py-3">
                <div class="spinner-border text-danger spinner-border-sm" role="status"></div>
                <span class="ms-2 text-secondary">Searching workshop live records...</span>
            </div>
        `;

        setTimeout(() => {
            const mockStatuses = ['IN_PROGRESS', 'READY_FOR_DELIVERY', 'PENDING_INSPECTION'];
            const randomStatus = mockStatuses[Math.abs(regInput.charCodeAt(0) || 0) % mockStatuses.length];

            let statusBadge = '';
            let statusText = '';
            let estTime = '';

            if (randomStatus === 'READY_FOR_DELIVERY') {
                statusBadge = '<span class="badge bg-success px-3 py-2 fs-6"><i class="bi bi-check-circle-fill me-1"></i> Ready for Delivery</span>';
                statusText = `Vehicle <strong>${regInput}</strong> has completed servicing and washing. You can collect it now.`;
                estTime = 'Ready Now';
            } else if (randomStatus === 'IN_PROGRESS') {
                statusBadge = '<span class="badge bg-warning text-dark px-3 py-2 fs-6"><i class="bi bi-tools me-1"></i> Servicing In Progress</span>';
                statusText = `Mechanic is currently tuning engine and inspecting oil filters for <strong>${regInput}</strong>.`;
                estTime = 'Estimated Completion: 45 Mins';
            } else {
                statusBadge = '<span class="badge bg-info text-dark px-3 py-2 fs-6"><i class="bi bi-hourglass-split me-1"></i> Queued for Service</span>';
                statusText = `Vehicle <strong>${regInput}</strong> is registered in the workshop queue. Service will begin shortly.`;
                estTime = 'Next in Queue';
            }

            statusResult.innerHTML = `
                <div class="p-3 rounded-3 bg-white text-dark mt-3 shadow-sm border">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <strong class="font-heading fs-5">${regInput}</strong>
                        ${statusBadge}
                    </div>
                    <p class="mb-2 text-secondary small">${statusText}</p>
                    <div class="d-flex justify-content-between align-items-center pt-2 border-top text-muted small">
                        <span><i class="bi bi-clock me-1"></i> ${estTime}</span>
                        <a href="tel:9352135105" class="text-danger fw-bold text-decoration-none"><i class="bi bi-telephone-fill me-1"></i> Call Workshop</a>
                    </div>
                </div>
            `;
        }, 600);
    });
});

/* ==========================================================================
   THREE.JS 3D BACKGROUND ENGINE
   ========================================================================== */
function initHero3DCanvas() {
    const canvas = document.getElementById('hero-3d-canvas');
    if (!canvas || typeof THREE === 'undefined') return;

    const parent = canvas.parentElement;
    let width = parent.clientWidth;
    let height = parent.clientHeight;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
    camera.position.z = 35;

    const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(width, height);

    // 1. Central Metallic Red Gear Ring
    const ringGeo1 = new THREE.TorusGeometry(12, 0.7, 16, 80);
    const ringMat1 = new THREE.MeshBasicMaterial({
        color: 0xE60012,
        wireframe: true,
        transparent: true,
        opacity: 0.35
    });
    const ringMesh1 = new THREE.Mesh(ringGeo1, ringMat1);
    ringMesh1.position.set(12, 0, -5);
    scene.add(ringMesh1);

    // 2. Outer Metallic Silver Ring
    const ringGeo2 = new THREE.TorusGeometry(18, 0.4, 16, 100);
    const ringMat2 = new THREE.MeshBasicMaterial({
        color: 0x94A3B8,
        wireframe: true,
        transparent: true,
        opacity: 0.25
    });
    const ringMesh2 = new THREE.Mesh(ringGeo2, ringMat2);
    ringMesh2.position.set(12, 0, -5);
    ringMesh2.rotation.x = Math.PI / 4;
    scene.add(ringMesh2);

    // 3. Floating 3D Mechanical Polyhedrons
    const polyGroup = new THREE.Group();
    const polyGeo = new THREE.IcosahedronGeometry(2.5, 1);
    const polyMat1 = new THREE.MeshBasicMaterial({ color: 0xE60012, wireframe: true, transparent: true, opacity: 0.4 });
    const polyMat2 = new THREE.MeshBasicMaterial({ color: 0x3B82F6, wireframe: true, transparent: true, opacity: 0.3 });

    for (let i = 0; i < 6; i++) {
        const poly = new THREE.Mesh(polyGeo, i % 2 === 0 ? polyMat1 : polyMat2);
        poly.position.set(
            (Math.random() - 0.5) * 50,
            (Math.random() - 0.5) * 30,
            (Math.random() - 0.5) * 20
        );
        poly.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);
        polyGroup.add(poly);
    }
    scene.add(polyGroup);

    // 4. Floating 3D Particle Cloud
    const particleCount = 180;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount * 3; i += 3) {
        positions[i] = (Math.random() - 0.5) * 70;
        positions[i + 1] = (Math.random() - 0.5) * 40;
        positions[i + 2] = (Math.random() - 0.5) * 30;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const particleMat = new THREE.PointsMaterial({
        color: 0xE60012,
        size: 0.4,
        transparent: true,
        opacity: 0.5
    });
    const particles = new THREE.Points(geometry, particleMat);
    scene.add(particles);

    // Mouse Interaction
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

    window.addEventListener('mousemove', (e) => {
        mouseX = (e.clientX - window.innerWidth / 2) * 0.001;
        mouseY = (e.clientY - window.innerHeight / 2) * 0.001;
    });

    // Animation Loop
    function animate() {
        requestAnimationFrame(animate);

        // Smooth rotation
        ringMesh1.rotation.x += 0.004;
        ringMesh1.rotation.y += 0.006;

        ringMesh2.rotation.x -= 0.003;
        ringMesh2.rotation.y += 0.005;

        polyGroup.children.forEach((poly, index) => {
            poly.rotation.x += 0.005 * (index % 2 === 0 ? 1 : -1);
            poly.rotation.y += 0.007;
        });

        particles.rotation.y += 0.001;

        // Smooth Mouse Parallax
        targetX += (mouseX - targetX) * 0.05;
        targetY += (mouseY - targetY) * 0.05;
        scene.rotation.y = targetX * 2;
        scene.rotation.x = -targetY * 2;

        renderer.render(scene, camera);
    }
    animate();

    // Resize Handler
    window.addEventListener('resize', () => {
        width = parent.clientWidth;
        height = parent.clientHeight;
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
    });
}

/* ==========================================================================
   3D CARD TILT EFFECT
   ========================================================================== */
function init3DCardTilt() {
    const cards = document.querySelectorAll('.card-3d-tilt, .service-package-card');
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = ((y - centerY) / centerY) * -8;
            const rotateY = ((x - centerX) / centerX) * 8;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
            card.style.transition = 'transform 0.1s ease-out';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
            card.style.transition = 'transform 0.5s ease-out';
        });
    });
}
