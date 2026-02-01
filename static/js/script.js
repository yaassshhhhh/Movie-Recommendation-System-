document.addEventListener('DOMContentLoaded', () => {
    const scrollTopBtn = document.getElementById('scrollTopBtn');
    const cardContainer = document.getElementById('cardContainer');
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const categorySelect = document.getElementById('categorySelect');
    const genreSelect = document.getElementById('genreSelect');
    const suggestionsBox = document.getElementById('suggestions');

    fetchMetadata();
    fetchMovies();

    function fetchMetadata() {
        fetch('/api/metadata')
            .then(res => res.json())
            .then(data => {
                populate(categorySelect, data.categories, 'All Categories');
                populate(genreSelect, data.genres, 'All Genres');
            });
    }

    function populate(select, items, text) {
        select.innerHTML = `<option value="All">${text}</option>`;
        items.forEach(i => {
            const o = document.createElement('option');
            o.value = i;
            o.textContent = i;
            select.appendChild(o);
        });
    }

    function fetchMovies(query = '') {
        fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query,
                category: categorySelect.value,
                genre: genreSelect.value
            })
        })
            .then(res => res.json())
            .then(renderCards);
    }

    function renderCards(movies) {
        cardContainer.innerHTML = '';

        if (movies.length === 0) {
            cardContainer.innerHTML = '<p>No results found</p>';
            return;
        }

        movies.forEach(movie => {
            const card = document.createElement('div');
            card.className = 'card';

            card.innerHTML = `
                <img src="${movie.Poster_URL}"
                     onerror="this.onerror=null;this.src='/static/images/placeholder.jpg';">
                <h3>${movie.Title}</h3>
                <p>${movie.Category} | ${movie.Genre}</p>
            `;

            cardContainer.appendChild(card);
        });
    }

    searchBtn.onclick = () => fetchMovies(searchInput.value);
    categorySelect.onchange = () => fetchMovies(searchInput.value);
    genreSelect.onchange = () => fetchMovies(searchInput.value);

    // --- Scroll to Top Button ---
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            scrollTopBtn.style.display = 'block';
        } else {
            scrollTopBtn.style.display = 'none';
        }
    });

    scrollTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });


    searchInput.addEventListener('input', () => {
        const q = searchInput.value.trim();
        if (!q) {
            suggestionsBox.innerHTML = '';
            return;
        }

        fetch(`/api/autocomplete?q=${q}`)
            .then(res => res.json())
            .then(data => {
                suggestionsBox.innerHTML = '';
                data.forEach(item => {
                    const li = document.createElement('li');
                    li.textContent = item;
                    li.onclick = () => {
                        searchInput.value = item;
                        suggestionsBox.innerHTML = '';
                        fetchMovies(item);
                    };
                    suggestionsBox.appendChild(li);
                });
            });
    });
});
