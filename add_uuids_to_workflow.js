
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const filename = process.argv[2] || 'n8n-workflows/workflow-v8-1-fixed.json';
const workflowPath = path.resolve(__dirname, filename);

try {
    const content = fs.readFileSync(workflowPath, 'utf8');
    const workflow = JSON.parse(content);

    if (workflow.nodes && Array.isArray(workflow.nodes)) {
        workflow.nodes.forEach(node => {
            // Generate a random UUID for each node if it doesn't have one
            if (!node.id) {
                node.id = crypto.randomUUID();
            }
        });
    }

    // Add meta info if missing
    if (!workflow.meta) {
        workflow.meta = {
            "instanceId": crypto.randomUUID() // Fake instance ID
        };
    }

    fs.writeFileSync(workflowPath, JSON.stringify(workflow, null, 2), 'utf8');
    console.log(`Successfully added UUIDs to all nodes in ${filename}`);

} catch (err) {
    console.error('Error processing workflow file:', err);
}
