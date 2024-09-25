body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f4f4f4;
}

header {
    background-color: #000000;
    color: white;
    text-align: center;
    padding: 1em;
}

main {
    background-color: white;
    padding: 20px;
    max-width: 800px;
    margin: 20px auto;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

#chat-container {
    display: flex;
    flex-direction: column;
    height: 70vh;
}

#log {
    flex: 1;
    overflow-y: auto;
    padding: 10px;
    border: 1px solid #ccc;
    margin-bottom: 10px;
    background-color: #f9f9f9;
}

#inputs {
    display: flex;
    justify-content: space-between;
}

#incident-number {
    flex: 0 0 20%;
    padding: 10px;
    margin-right: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
}

#user-input {
    flex: 1;
    padding: 10px;
    margin-right: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
}

#inputs button {
    padding: 10px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

#inputs button:hover {
    background-color: #45a049;
}

.user-message {
    text-align: right;
    margin: 5px 0;
    background-color: #e1ffc7;
    padding: 10px;
    border-radius: 4px;
    word-wrap: break-word;
}

.gpt-response {
    text-align: left;
    margin: 5px 0;
    background-color: #f1f1f1;
    padding: 10px;
    border-radius: 4px;
    word-wrap: break-word;
    white-space: pre-wrap; /* Ensure preformatted text is displayed correctly */
}

.gpt-response a {
    color: #1a0dab;
    text-decoration: none;
}

.gpt-response a:hover {
    text-decoration: underline;
}

.gpt-response strong {
    font-weight: bold;
}

.gpt-response em {
    font-style: italic;
}

.gpt-response pre {
    background-color: #f4f4f4;
    padding: 10px;
    border-radius: 4px;
    overflow-x: auto;
}

.gpt-response code {
    background-color: #f4f4f4;
    padding: 2px 4px;
    border-radius: 4px;
}