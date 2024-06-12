function piechart(string, xdata, ydata){
const xValues = xdata;
const yValues = ydata;
const barColors = ["black", "grey","lightsteelblue", "lightgreen", "lightcoral"];


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

