const API_URL = '/api';

function uploadVideo() {
    const fileInput = document.getElementById('videoFile');
    const operation = document.getElementById('operation').value;
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a video file');
        return;
    }
    
    // Simulate file upload and job creation
    const inputFilename = file.name;
    const outputFilename = generateOutputFilename(file.name, operation);
    
    fetch(`${API_URL}/jobs`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            input_filename: inputFilename,
            output_filename: outputFilename,
            operation: operation
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('status').innerHTML = 
            `<p>Job created: ${data.job_id}</p>`;
        loadJobs();
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('status').innerHTML = 
            `<p style="color: red">Error creating job</p>`;
    });
}

function generateOutputFilename(inputFilename, operation) {
    const name = inputFilename.split('.')[0];
    const extension = operation === 'thumbnail' ? 'jpg' : 'mp4';
    return `${name}_${operation}.${extension}`;
}

function loadJobs() {
    fetch(`${API_URL}/jobs`)
    .then(response => response.json())
    .then(jobs => {
        const jobsDiv = document.getElementById('jobs');
        jobsDiv.innerHTML = '';
        
        jobs.forEach(job => {
            const jobDiv = document.createElement('div');
            jobDiv.className = 'job';
            jobDiv.innerHTML = `
                <strong>${job.input_filename}</strong> → ${job.output_filename}
                <span class="status ${job.status}">${job.status.toUpperCase()}</span>
                <br>
                <small>Operation: ${job.operation} | Created: ${job.created_at}</small>
                ${job.message ? `<br><small>Message: ${job.message}</small>` : ''}
            `;
            jobsDiv.appendChild(jobDiv);
        });
    });
}

// Load jobs on page load
window.onload = function() {
    loadJobs();
    // Refresh jobs every 5 seconds
    setInterval(loadJobs, 5000);
};
