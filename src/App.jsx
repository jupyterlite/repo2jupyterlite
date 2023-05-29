import { useState } from "react";
import { createRoot } from "react-dom/client";
import "bootstrap/dist/css/bootstrap.min.css";

import { parseRepoURL } from "./detectors";

import "./App.css";

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
    </div>
  );
}

document.body.innerHTML = "<div id='app'></div>";
const root = createRoot(document.getElementById("app"));
root.render(<App />);
