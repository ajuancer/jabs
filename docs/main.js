function reportWindowSize() {
  document.getElementById("middle-photo").style.width= (document.documentElement.clientWidth*.8)+"px"
  document.getElementById("middle-photo").style.height= (document.documentElement.clientHeight*.8)+"px"
}
reportWindowSize()

window.addEventListener('resize', reportWindowSize);
var x = "Total Width: " + document.documentElement.clientWidth; 
console.log(x);
