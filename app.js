async function fetchAndRenderProperties() {
    const container = document.getElementById('properties-container');
    container.innerHTML = '<div style="padding: 20px; color: var(--accent);">Cargando casas reales...</div>';

    try {
        const response = await fetch('backend/propiedades_totales.json');
        const data = await response.json();
        
        container.innerHTML = '';
        let matchCount = 0;

        data.forEach(prop => {
            // Estandarizar campos ya que provienen de distintos scrapers
            const portal = prop.portal || prop.origen || 'Desconocido';
            const link = prop.link || prop.url || '#';
            const beds = parseInt(prop.beds || prop.habitaciones) || 0;
            const baths = parseInt(prop.baths || prop.banos) || 0;
            const area = prop.area || prop.superficie || 'N/A';
            const image = prop.image || prop.imagen || '';
            const desc = (prop.descripcion || '').toLowerCase();
            const titulo = (prop.titulo || '').toLowerCase();

            // Limpiar y parsear el precio
            let priceNum = 0;
            const priceStr = String(prop.precio || '').replace(/\./g, '');
            const priceMatch = priceStr.match(/(\d+)/);
            if (priceMatch && (priceStr.toUpperCase().includes('US$') || priceStr.toUpperCase().includes('USD'))) {
                priceNum = parseInt(priceMatch[1]);
            }

            // Filtros Semánticos
            const fullText = titulo + " " + desc;
            const hasJardin = fullText.includes('jardin') || fullText.includes('jardín') || fullText.includes('patio');
            const aptoCredito = fullText.includes('apta credito') || fullText.includes('apto credito') || fullText.includes('apta crédito') || fullText.includes('crédito hipotecario');
            const noAptoCredito = fullText.includes('no apta') || fullText.includes('no apto');
            
            const isAptoCredito = aptoCredito && !noAptoCredito;

            // Aplicar Filtros Duros: 50k a 90k, 3+ habs, 2+ baños, Jardin, Apta Credito
            // Si el precio es 0, a veces no lo traen bien, podemos omitir o mostrar. Lo filtramos estrictamente.
            
            let isMatch = false;
            let isPartial = false;
            
            if (priceNum >= 50000 && priceNum <= 90000 && beds >= 3 && baths >= 2 && hasJardin) {
                isMatch = true;
            } else if (priceNum > 0 && priceNum <= 130000 && beds >= 2) {
                isPartial = true;
            }

            // Aplicar estrictamente los filtros solicitados por el usuario
            if (isMatch || isPartial) {
                if (isMatch) matchCount++;
                const card = document.createElement('div');
                card.className = 'property-card';
                // Add an opacity or styling to partial matches to differentiate
                if (isPartial) {
                    card.style.opacity = '0.85';
                    card.style.border = '1px solid #444';
                }
                
                const randomImg = image && image !== "#" ? image : `https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80`;

                let matchBadge = isMatch ? 
                    '<span class="match-badge" style="background:var(--accent); color:#000;">Match Exacto</span>' : 
                    '<span class="match-badge" style="background:#6c757d; color:#fff;">Match Parcial</span>';
                
                let tagsHtml = '';
                if (isAptoCredito) tagsHtml += '<span class="tag credit" style="background:#28a745; color:white;">Apta Crédito ✅</span>';
                if (hasJardin) tagsHtml += '<span class="tag" style="background:#20c997; color:white;">Tiene Jardín 🌳</span>';

                card.innerHTML = `
                    <div class="prop-img-container">
                        <span class="portal-badge">${portal}</span>
                        ${matchBadge}
                        <img src="${randomImg}" alt="Casa" onerror="this.src='https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80'">
                    </div>
                    <div class="prop-info">
                        <div class="prop-price">${prop.precio}</div>
                        <h3 class="prop-title">${prop.titulo}</h3>
                        
                        <div class="prop-features">
                            <span>🛏️ ${beds} hab</span>
                            <span>🛁 ${baths} ba</span>
                            <span>📐 ${area}</span>
                        </div>

                        <div class="tags">
                            ${tagsHtml}
                        </div>

                        <div class="prop-actions">
                            <a href="${link}" class="btn-view" target="_blank">Ver en ${portal}</a>
                            <button class="btn-discard" onclick="this.closest('.property-card').remove()" title="Descartar">🗑️</button>
                        </div>
                    </div>
                `;
                container.appendChild(card);
            }
        });

        if (container.innerHTML === '') {
            container.innerHTML = '<div style="padding: 20px; color: var(--text-muted);">No se encontraron casas ni siquiera como match parcial.</div>';
        }

        // Actualizar estadísticas del dashboard
        document.querySelector('.stat-card.highlight .stat-value').textContent = matchCount;
        document.querySelector('.stat-card:first-child .stat-value').textContent = data.length;

    } catch (error) {
        console.error("Error al cargar JSON:", error);
        container.innerHTML = '<div style="padding: 20px; color: var(--red);">Error al leer los datos consolidados. Ejecuta el orquestador backend.</div>';
    }
}

document.getElementById('btn-sync').addEventListener('click', (e) => {
    const btn = e.currentTarget;
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="sync-icon" style="animation: spin 1s linear infinite">⚙️</span> Sincronizando...';
    
    setTimeout(() => {
        fetchAndRenderProperties();
        btn.innerHTML = originalText;
    }, 1000);
});

// Render inicial
fetchAndRenderProperties();
