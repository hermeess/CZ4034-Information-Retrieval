from django.shortcuts import render
import json

def pie_chart(request, labels, values):
    # Convert labels and values to JSON format
    data = json.dumps({'labels': labels, 'values': values})
    return render(request, 'myapp/pie_chart.html', {'data': data})
