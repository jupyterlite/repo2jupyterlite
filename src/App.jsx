import { useState } from "react";
import { createRoot } from "react-dom/client";
import "bootstrap/dist/css/bootstrap.min.css";

import { parseRepoURL } from "./detectors";

import "./App.css";

function App() {
  const [repoUrl, setRepoUrl] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [detectedInfo, setDetectedInfo] = useState(null);
  return (
    <div className="container">
      <div className="text-center" id="logo">
        <img src="/static/wordmark.svg" width="640" />
      </div>
      <form id="build-form" className="form">
        <div className="row">
          <div className="form-group col-sm-10">
            <label>Repository to Build</label>
            <input
              className="form-control"
              type="text"
              style={{ fontSize: "16px" }}
              name="spec"
              id="spec"
              value={repoUrl}
              onChange={(e) => {
                const parsedRepo = parseRepoURL(e.target.value);
                setDetectedInfo(parsedRepo);
                console.log(parsedRepo);
                setRepoUrl(e.target.value);
              }}
            />
          </div>
          <div className="form-group col-sm d-flex align-items-end">
            <input
              id="submit"
              className="form-control btn btn-primary"
              type="button"
              style={{ fontSize: "16px" }}
              value={isSubmitting ? "Building..." : "Launch"}
              disabled={!Boolean(detectedInfo)}
              onClick={() => {
                const redirectUrl = `/v1/${detectedInfo.spec}`;
                setIsSubmitting(true);

                window.location.href = redirectUrl;
                return false;
              }}
            />
          </div>
        </div>
        <div className="row parsed-url-container">
          <ul className="">
            {detectedInfo &&
              Object.keys(detectedInfo.displayParts).map((key) => {
                return (
                  <li key={key} className="list-group-item">
                    <span>{key}</span>:{" "}
                    <strong>{detectedInfo.displayParts[key]}</strong>
                  </li>
                );
              })}
          </ul>
        </div>
      </form>
    </div>
  );
}

const A = () => {
  const [a, setA] = useState("hi");
};

const root = createRoot(document.getElementById("app"));
root.render(<App />);
