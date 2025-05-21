document.getElementById('toggleSidebarBtn').addEventListener('click', function () {
    document.getElementById('sidebar').classList.toggle('show');
    document.getElementById('overlay').classList.toggle('show');
  });

document.getElementById('lupa').addEventListener('click', function () {
    document.getElementById('sidebar').classList.toggle('show');
    document.getElementById('overlay').classList.toggle('show');
  });

  document.querySelector('.close-btn').addEventListener('click', function () {
    document.getElementById('sidebar').classList.remove('show');
    document.getElementById('overlay').classList.remove('show');
  });

  document.getElementById('overlay').addEventListener('click', function() {
    document.getElementById('sidebar').classList.remove('show');
    document.getElementById('overlay').classList.remove('show');
  })