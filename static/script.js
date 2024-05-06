// Dark Mode Toggle
const darkModeToggle = document.querySelector('#dark-mode-toggle');
const body = document.body;

darkModeToggle.addEventListener('click', () => {
  body.classList.toggle('dark-mode');
});

// Fetch weather data (including news and alerts) on page load
window.onload = function () {
    fetchWeatherData();
    setInterval(fetchWeatherData, 300000); // Update weather data every 5 minutes
};

function fetchWeatherData() {
    fetch('/predict') // Replace with your actual Flask route for fetching weather data
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        // Check if the response is JSON before parsing
        if (response.headers.get('Content-Type').includes('application/json')) {
          return response.json();
        } else {
          // Handle non-JSON response (optional: display an error message)
          console.error('Unexpected response format. Expected JSON data.');
          // You can throw an error here to stop further processing
          // throw new Error('Unexpected response format');
        }
      })
      .then(data => {
        // Update weather data on the page
        document.querySelector('.weather-description').textContent = capitalizeFirstLetter(data.weather_data.description);
        document.querySelector('.temperature').textContent = `${data.weather_data.temperature.toFixed(1)}°C`;

        // Update weather icon
        let weatherIcon = document.querySelector('.weather-icon');
        function getWeatherImageName(weather) {
          switch (weather.toLowerCase()) {
            case 'clear':
              return 'sunny.png';
            case 'clouds':
              return 'cloudy.png';
            case 'rain':
              return 'rainy.png';
            case 'wind':
              return 'windy.png';
            default:
              return 'unknown.png'; // Optional: Image for unknown weather
          }
        }

        const weatherImageName = getWeatherImageName(data.weather_data.weather);
        weatherIcon.src = `./static/weather-icons/${weatherImageName}`;

        // Update news content if available
        if (data.news_data) {
          document.querySelector('.news-title').textContent = data.news_data.title; // Assuming news data has a "title" property
          document.querySelector('.news-description').textContent = data.news_data.description; // Assuming news data has a "description" property
          // You can also update other news elements like the link
        } else {
          document.querySelector('.news-title').textContent = 'No news available';
        }

        // Update weather alerts if available
        if (data.weather_alerts) {
          const weatherAlertsContainer = document.querySelector('.weather-alerts');
          weatherAlertsContainer.innerHTML = ''; // Clear previous alerts

          data.weather_alerts.forEach(alert => {
            const alertElement = document.createElement('div');
            alertElement.classList.add('weather-alert');
            alertElement.innerHTML = `
              <h3>${alert.title}</h3>
              <p>${alert.description}</p>
            `;
            weatherAlertsContainer.appendChild(alertElement);
          });
        } else {
          const weatherAlertsContainer = document.querySelector('.weather-alerts');
          weatherAlertsContainer.innerHTML = '<p>No weather alerts available.</p>';
        }
      })
      .catch(error => {
        console.error('Error fetching weather data:', error);
        // Handle errors (e.g., display an error message to the user)
      });
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}