/**
 * Detect what repo provider given URL is and get a spec
 */

class ParsedRepoURL {
  provider;
  displayParts;
  spec;

  constructor(provider, spec, displayParts) {
    this.displayParts = displayParts;
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
  if (pathParts.length === 2) {
    // path is like <username>/<reponame>
    // So reponame is present, ref is not
    return new ParsedRepoURL("gh", `gh/${pathParts[0]}/${pathParts[1]}/HEAD`, {
      source: url.hostname,
      repository: `${pathParts[0]}/${pathParts[1]}`,
      ref: "default branch",
    });
  } else if (pathParts.length >= 4) {
    // path is like <username>/<reponame>/tree|blob|commit/<ref>/<path-to-file>
    if (
      pathParts[2] === "tree" ||
      pathParts[2] === "commit" ||
      pathParts[2] === "blob"
    ) {
      return new ParsedRepoURL(
        "gh",
        `gh/${pathParts[0]}/${pathParts[1]}/${pathParts[3]}`,
        {
          source: url.hostname,
          repository: `${pathParts[0]}/${pathParts[1]}`,
          ref: pathParts[3],
        },
      );
    }
  }
}
