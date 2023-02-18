let storedTheme = localStorage.getItem('theme');

if (storedTheme === 'light') {
  jtd.setTheme(storedTheme);
}
