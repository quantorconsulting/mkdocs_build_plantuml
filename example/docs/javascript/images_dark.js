if (window.matchMedia('(prefers-color-scheme: dark)').matches === true) {
  var darkables = document.querySelectorAll('img[src$="darkable"');
  fromLightToDark(darkables);
}

const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
darkModeMediaQuery.addListener((e) => {
  const darkModeOn = e.matches;
  var darkables = document.querySelectorAll('img[src$="darkable"');

  if (darkModeOn)
    fromLightToDark(darkables);
  else
    fromDarkToLight(darkables);
  console.log(`Dark mode is ${darkModeOn ? '🌒 on' : '☀️ off'}.`);
});

function fromLightToDark(images) {
  images.forEach(image => {
    var idx = image.src.lastIndexOf('.');
    if (idx > -1) {
      var add = "_dark";
      image.src = [image.src.slice(0, idx), add, image.src.slice(idx)].join('');
    }
  });
}

function fromDarkToLight(images) {
  images.forEach(image => {
    image.src = image.src.replace("_dark", "");
  });
}