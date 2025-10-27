(function () {
        // --- Element Selectors ---
        const locationInput = document.getElementById('location-input');
        const getLocationBtn = document.getElementById('get-location-btn');
        const addressSearch = document.getElementById('address-search');
        const searchBtn = document.getElementById('search-btn');
        const mapContainer = document.getElementById('location-map');
        const mapInstruction = document.getElementById('map-instruction');
        const locationModal = document.getElementById('location-modal');
        const detectedLocationText = document.getElementById('detected-location');
        const confirmLocationBtn = document.getElementById('confirm-location');
        const cancelLocationBtn = document.getElementById('cancel-location');
        const issueTypeSelect = document.getElementById('issue-type');
        const otherIssueContainer = document.getElementById('other-issue-container');
        const fileUpload = document.getElementById('file-upload');
        const previewContainer = document.getElementById('image-preview-container');

        // --- Map State Variables ---
        let map;
        let marker;

        // --- Core Functions ---
        
        // NEW: Central function to update UI elements based on coordinates
        async function updateLocationUI(lat, lng) {
            // Give visual feedback while fetching address
            locationInput.value = 'Fetching address...';
            
            const address = await reverseGeocode(lat, lng);
            
            // Update input field and hidden data attributes
            locationInput.value = address;
            locationInput.setAttribute('data-latitude', String(lat));
            locationInput.setAttribute('data-longitude', String(lng));
            
            // Move the marker to the new position
            if (marker) {
                marker.setLatLng([lat, lng]);
            }
        }

        // Reverse geocodes coordinates to a human-readable address
        async function reverseGeocode(lat, lng) {
            const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`;
            try {
                const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
                const data = await res.json();
                return data.display_name || `Lat: ${lat.toFixed(4)}, Lon: ${lng.toFixed(4)}`;
            } catch {
                return `Lat: ${lat.toFixed(4)}, Lon: ${lng.toFixed(4)}`;
            }
        }

        // Falls back to IP-based location if GPS fails or is denied
        async function ipFallback() {
            try {
                const res = await fetch('https://ipapi.co/json/');
                const data = await res.json();
                if (data && typeof data.latitude === 'number' && typeof data.longitude === 'number') {
                    return { lat: data.latitude, lng: data.longitude };
                }
            } catch {}
            return null;
        }

        // Initializes the map and sets the initial location
        async function setInitialLocation(lat, lng) {
            // Show map and instructions
            mapContainer.classList.remove('hidden');
            mapInstruction.classList.remove('hidden');

            if (!map) {
                // Create map
                map = L.map('location-map').setView([lat, lng], 16);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                }).addTo(map);

                // Create a DRAGGABLE marker
                marker = L.marker([lat, lng], { draggable: true }).addTo(map);

                // --- NEW EVENT LISTENERS for interactive map ---
                // 1. Update location when marker is dragged and dropped
                marker.on('dragend', function(e) {
                    const { lat, lng } = e.target.getLatLng();
                    updateLocationUI(lat, lng);
                });
                
                // 2. Update location when user clicks on the map
                map.on('click', function(e) {
                    const { lat, lng } = e.latlng;
                    map.panTo(e.latlng); // Smoothly center map on click
                    updateLocationUI(lat, lng);
                });
            }
            
            // Update UI with the found location
            await updateLocationUI(lat, lng);

            // Show confirmation modal
            detectedLocationText.textContent = locationInput.value;
            locationModal.classList.add('is-active');
        }

        // Tries to get GPS location, with fallback
        async function getLocation() {
            if (!navigator.geolocation) {
                const ip = await ipFallback();
                if (ip) return setInitialLocation(ip.lat, ip.lng);
                alert('Geolocation not supported, and IP fallback failed. Please enter your address manually.');
                return;
            }
            navigator.geolocation.getCurrentPosition(async (pos) => {
                await setInitialLocation(pos.coords.latitude, pos.coords.longitude);
            }, async () => {
                const ip = await ipFallback();
                if (ip) await setInitialLocation(ip.lat, ip.lng);
                else alert('Unable to get your location. Please type your address.');
            }, { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 });
        }

        // Searches for an address using Nominatim API
        async function searchAddress(query) {
            if (!query || !query.trim()) return;
            try {
                const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`;
                const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
                const data = await res.json();
                if (Array.isArray(data) && data.length > 0) {
                    const match = data[0];
                    await setInitialLocation(Number(match.lat), Number(match.lon));
                } else {
                    alert('No results found for that address.');
                }
            } catch (e) {
                console.error('Search failed', e);
                alert('Address search failed. Please try again.');
            }
        }

        // --- Event Listener Assignments ---
        
        // Auto-attempt location on page load
        document.addEventListener('DOMContentLoaded', () => { /* Auto-fetch is now optional, user can click */ });
        
        // GPS button click
        getLocationBtn?.addEventListener('click', async function () {
            this.innerHTML = `<span class="spinner"></span><span class="hidden sm:inline ml-1">GPS</span>`;
            this.disabled = true;
            await getLocation();
            this.innerHTML = `<span class="material-icons text-sm">my_location</span><span class="hidden sm:inline ml-1">GPS</span>`;
            this.disabled = false;
        });
        
        // Address search button and enter key
        if (addressSearch && searchBtn) {
            searchBtn.addEventListener('click', () => searchAddress(addressSearch.value));
            addressSearch.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') { e.preventDefault(); searchAddress(addressSearch.value); }
            });
        }
        
        // Location modal buttons
        confirmLocationBtn?.addEventListener('click', () => locationModal.classList.remove('is-active'));
        cancelLocationBtn?.addEventListener('click', () => locationModal.classList.remove('is-active'));
        
        // "Other Issues" dropdown logic
        issueTypeSelect?.addEventListener('change', function () {
            otherIssueContainer.style.display = (this.value === 'Other Issues') ? 'block' : 'none';
        });

        // File upload with preview
        if (fileUpload && previewContainer) {
            fileUpload.addEventListener('change', function (event) {
                if (event.target.files.length > 3) {
                    alert('You can only upload a maximum of 3 images.');
                    this.value = '';
                    return;
                }
                previewContainer.innerHTML = '';
                Array.from(event.target.files).forEach(file => {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        const previewWrapper = document.createElement('div');
                        previewWrapper.className = 'relative group';
                        previewWrapper.innerHTML = `
                            <img src="${e.target.result}" class="w-full h-24 object-cover rounded-md border border-border-light dark:border-border-dark" alt="Image preview">
                            <button type="button" class="remove-btn absolute top-1 right-1 bg-red-600 text-white rounded-full h-6 w-6 flex items-center justify-center text-lg font-bold opacity-0 group-hover:opacity-100 transition-opacity">&times;</button>
                        `;
                        previewContainer.appendChild(previewWrapper);
                    };
                    reader.readAsDataURL(file);
                });
            });
            previewContainer.addEventListener('click', function (e) {
                if (e.target && e.target.classList.contains('remove-btn')) {
                    e.target.parentElement.remove();
                }
            });
        }
    })();