var app = new Framework7({
  root: '#app',
  // App Name
  name: 'Ride-a-Bike',
  // App id
  id: 'app.ride-a-bike.com',
  // Enable swipe panel
  panel: {
    swipe: 'left',
  }
});

var mainView = app.views.create('.view-main');