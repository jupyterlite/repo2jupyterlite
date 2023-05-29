/**
 * Detect what repo provider given URL is and get a spec
 */

class ParsedRepoURL {
  provider;
  displayParts;
  spec;
  filePath;

  constructor(provider, spec, filePath, displayParts) {
    this.displayParts = displayParts;
    this.filePath = filePath;
    this.provider = provider;
    this.spec = spec;
  }
}

/**
 *
 * @param {string} url
 * @returns {ParsedRepoURL}
 */
export function parseRepoURL(url) {
  const funcs = [github];

  let urlObj;
  try {
    urlObj = new URL(url);
  } catch (e) {
    console.log(e);
    return null;
  }

  for (const f of funcs) {
    const ret = f(urlObj);
    if (ret) {
      return ret;
    }
  }
}

/**
 *
 * @param {URL} url
 */
function github(url) {
  // FIXME: This should be configurable!
  if (url.hostname !== "github.com") {
    return null;
  }
  const pathParts = url.pathname
    .split("/")
    .filter((part) => part.trim() !== "");
  if (pathParts.length < 2) {
    return null;
  }
  let parts = {
    user: pathParts[0],
    repo: pathParts[1],
    ref: "HEAD",
    filePath: "",
  };

  // Only check for ref if path is like <user>/<repo>/<kind>/<ref>
  if (
    pathParts.length > 3 &&
    ["blob", "tree", "commit"].includes(pathParts[2])
  ) {
    parts["ref"] = pathParts[3];
    if (pathParts.length > 4) {
      parts["filePath"] = pathParts.slice(4).join("/");
    }
  }
  return new ParsedRepoURL(
    "gh",
    `gh/${parts.user}/${parts.repo}/${parts.ref}`,
    parts.filePath,
    {
      source: url.hostname,
      repository: `${parts.user}/${parts.repo}`,
      ref: parts.ref === "HEAD" ? "default branch" : parts.ref,
      "path to open": parts.filePath,
    },
  );
}
