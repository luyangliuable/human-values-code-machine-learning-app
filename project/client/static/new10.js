// custom javascript

(function() {
    console.log('Sanity Check!11');})();

function handleClick(type) {
    var file = document.getElementById('a').files;
    window.alert(JSON.stringify(file));
    fetch('/tasks', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ type: type, 'file': file }),
    }).then(response => response.json()).then(data => getStatus(data.task_id));
}


function getStatus(taskID) {
    fetch(`/tasks/${taskID}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
    })
        .then(response => response.json())
        .then(res => {
            const html = `
      <tr>
        <td>${taskID}</td>
        <td>${res.task_status}</td>
        <td>${res.task_result}</td>
      </tr>`;
            const newRow = document.getElementById('tasks').insertRow(0);
            newRow.innerHTML = html;

            const taskStatus = res.task_status;
            if (taskStatus === 'SUCCESS' || taskStatus === 'FAILURE') return false;
            setTimeout(function() {
                getStatus(res.task_id);
            }, 1000);
        }).catch(err => console.log(err));
}
