import { useState } from "react";
import { createRoot } from "react-dom/client";
import "bootstrap/dist/css/bootstrap.min.css";

import { parseRepoURL } from "./detectors";

import "./App.css";

function ExplanatoryCards() {
  return (
    <div className="row">
      <h3 className="text-center explanatory-card-header">How it works</h3>
      <div className="card border-light col-sm-4 text-center explanatory-card">
        <div className="card-body">
          <h4 className="card-title">1. Enter your repo information</h4>
          <p className="card-text">
            Provide a URL to the GitHub repository you want to launch. You can
            point to a specific branch or commit, along with a specific notebook
            you want to launch!
          </p>
        </div>
      </div>
      <div className="card border-light col-sm-4 text-center explanatory-card">
        <div className="card-body">
          <h4 className="card-title">2. We pre-install Python Packages</h4>
          <p className="card-text">
            We look for an{" "}
            <code>
              <strong>environment.yml</strong>
            </code>{" "}
            file in your repository, and any packages found listed there are
            installed. Your users can start using these packages immediately
            once JupyterLite loads.
          </p>
        </div>
      </div>
      <div className="card border-light col-sm-4 text-center explanatory-card">
        <div className="card-body">
          <h4 className="card-title">3. Interact with your repo!</h4>
          <p className="card-text">
            You can open notebooks, execute code and test everything out! Simply
            share that link with anyone else for them to have access to the same
            content!
          </p>
        </div>
      </div>

      <div className="text-center m-5 p-5">
        <small style={{ color: "#999" }}>
          Provide feedback{" "}
          <a href="https://github.com/jupyterlite/repo2jupyterlite">
            on GitHub
          </a>
          . Made with ❤️ by <a href="https://yuvi.in">Yuvi</a>
        </small>
      </div>
    </div>
  );
}

function App() {
  const [repoUrl, setRepoUrl] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [parsedRepoURL, setParsedRepoURL] = useState(null);
  return (
    <div className="container">
      <div className="text-center" id="logo">
        <img src="/static/wordmark.svg" width="640" />
      </div>
      <form id="build-form" className="form">
        <div className="row">
          <div className="form-group">
            <input
              autoFocus={true}
              className="form-control"
              type="text"
              style={{ fontSize: "20px" }}
              name="spec"
              id="spec"
              placeholder="Enter GitHub URL"
              value={repoUrl}
              onChange={(e) => {
                const parsedRepo = parseRepoURL(e.target.value);
                setParsedRepoURL(parsedRepo);
                console.log(parsedRepo);
                setRepoUrl(e.target.value);
              }}
            />
          </div>
        </div>
        <div className="row parsed-url-container">
          <div className="col-sm-10">
            <ul>
              {parsedRepoURL &&
                Object.keys(parsedRepoURL.displayParts).map((key) => {
                  if (parsedRepoURL.displayParts[key]) {
                    return (
                      <li key={key}>
                        <span>{key}</span>:{" "}
                        <strong>{parsedRepoURL.displayParts[key]}</strong>
                      </li>
                    );
                  }
                })}
            </ul>
          </div>
          <div className="form-group col-sm d-flex align-items-end">
            <input
              id="submit"
              className="form-control btn btn-primary"
              type="button"
              style={{ fontSize: "16px" }}
              value={isSubmitting ? "Building..." : "Launch"}
              disabled={!Boolean(parsedRepoURL)}
              onClick={() => {
                let redirectUrl = new URL(
                  `${window.location.protocol}//${window.location.host}/v1/${parsedRepoURL.spec}`,
                );
                if (parsedRepoURL.filePath) {
                  redirectUrl.searchParams.append(
                    "path",
                    parsedRepoURL.filePath,
                  );
                }
                setIsSubmitting(true);

                window.location.href = redirectUrl;
                return false;
              }}
            />
          </div>
        </div>
      </form>
      <ExplanatoryCards />
    </div>
  );
}

document.body.innerHTML = "<div id='app'></div>";
const root = createRoot(document.getElementById("app"));
root.render(<App />);
