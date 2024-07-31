function piechart(string, xdata, ydata){
const xValues = xdata;
const yValues = ydata;
const barColors = ["#8ecae6", "#d62828","#219ebc", "#023047", "#ffb703", "#fb8500"];


var element = document.getElementById(string);
new Chart(element, {
  type: "pie",
  data: {
    labels: xValues,
    datasets: [{
      backgroundColor: barColors,
      data: yValues
    }]
  },
  options: {
    legend: {display: true},
    title: {
      display: true,
    }
  }
});
}

function show(id){
  var trigger = event.srcElement;

  if (trigger.id != 0)
  {
      document.getElementById(id).style.display = 'table-row';
  }

}

