var app = new Framework7({
  root: '#app',
  // App Name
  name: 'Ride-a-Bike',
  // App id
  id: 'ride-a-bike.paper.app',
  // Enable swipe panel
  panel: {
    swipe: 'left',
  }
});

var mainView = app.views.create('.view-main');