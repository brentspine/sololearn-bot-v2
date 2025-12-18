// MADE BY BRENTSPINE
// This script is for following OTHER people's account. The rest of the repo is about follow-botting
// Educational purposes only, do not abuse

// Upper bound -> new users, more attention
// Lower bound -> So eventually all users on the site get hit

UPPER_BOUND_FOLLOW_RETRIES = 15;          // How many upper bound account ids to go forward
TRY_UPPER_BOUND_TIMEOUT_SECONDS = 3*60;   // How often the script rechecks the upper bound
STARTED_AT_UPPER_BOUND = 35087148;        // The start for the upper bound system

// PUT YOUR REFRESH TOKEN HERE
REFRESH_TOKEN = "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJzaWQiOiJ7XCJJbnN0YW5jZUlkXCI6NTE0NzIzNTksXCJVc2VySWRcIjozMzk2NTU2OSxcIk5pY2tuYW1lXCI6XCJCcmVudHNwaW5lXCIsXCJEZXZpY2VJZFwiOjk2ODc1MTkzLFwiQ2xpZW50SWRcIjoxMTQzLFwiUGxhdGZvcm1JZFwiOjQsXCJMb2NhbGVJZFwiOjEsXCJBcHBWZXJzaW9uXCI6XCIwLjAuMC4wXCIsXCJJc1Byb1wiOmZhbHNlLFwiUGxhbkNvbmZpZ3VyYXRpb25JZFwiOjEsXCJDb250ZXh0SWRcIjoxLFwiT3JnYW5pemF0aW9uSWRcIjowLFwiR2VuZXJhdGlvblwiOlwiZGQ1YjIyYzItNGQ0NC00MzFjLTg4MjItNTkwOWNjZjk4YTAxXCIsXCJDb3VudHJ5Q29kZVwiOlwiREVcIn0iLCJqdGkiOiIyMjRkYTRlMi04OTIwLTQ5NzEtYTRlZC01NDY1ZWExN2Y4NzkiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJVc2VyIiwibmJmIjoxNzY2MDI5MjkwLCJleHAiOjE3NzM4MDUyOTAsImlzcyI6IlNvbG9MZWFybi5TZWN1cml0eS5CZWFyZXIiLCJhdWQiOiJTb2xvTGVhcm4uU2VjdXJpdHkuUmVmcmVzaCJ9.VuPYyVJSpx8DpF3HCh7xxDXmjdEOvSui1aSKUiqofZe4axqUJowXAqb7ae24qqh7vXaaztnbBY47sdiCBVQ0Cg";

class Data {
	constructor() {
		this._latestUpperBoundFollow = Number(localStorage.getItem("latestUpperBoundFollow") ?? STARTED_AT_UPPER_BOUND);
		this._latestLowerBoundFollow = Number(localStorage.getItem("latestLowerBoundFollow") ?? 1);
	}

	get latestUpperBoundFollow() {
		return this._latestUpperBoundFollow;
	}
	set latestUpperBoundFollow(value) {
		this._latestUpperBoundFollow = Number(value);
		localStorage.setItem("latestUpperBoundFollow", String(this._latestUpperBoundFollow));
	}

	get latestLowerBoundFollow() {
		return this._latestLowerBoundFollow;
	}
	set latestLowerBoundFollow(value) {
		this._latestLowerBoundFollow = Number(value);
		localStorage.setItem("latestLowerBoundFollow", String(this._latestLowerBoundFollow));
	}
	
}

const ErrorType = {
	USER_NOT_FOUND: "USER_NOT_FOUND",
	RATE_LIMITED: "RATE_LIMITED",
	UNKNOWN: "UNKNOWN",
	UNAUTHORIZED: "UNAUTHORIZED",
};

async function main() {
	// Make sure we actually hit everyone by decreasing on refresh
	(new Data())._latestUpperBoundFollow -= 3;
	(new Data())._latestLowerBoundFollow -= 3;
	checkTokenRefresh();
	await sleep(500);
	while(true) {
		if(!(await upperBoundLoop())) break;
		if(STARTED_AT_UPPER_BOUND >= (new Data())._latestLowerBoundFollow)
			if(!(await lowerBoundLoop())) break;
	}
	console.log("UNAUTHORIZED");
}
main();

async function lowerBoundLoop() {
	const start = getSeconds();
	const end = start + TRY_UPPER_BOUND_TIMEOUT_SECONDS;
	while(true) {
		const success = await followLowerBound();
		console.log(success);
		if(success == null) return false;
		console.clear();
		if(end <= getSeconds()) {
			console.log(`Starting upperBoundLoop ( ${TRY_UPPER_BOUND_TIMEOUT_SECONDS}s elapsed)`);
			return true;
		}
	}
	return true;
}
function getSeconds() {
	return new Date().getTime() / 1000;
}

async function upperBoundLoop() {
	const data = new Data();
	let failedAttempts = 0;
	while(true) {
		const success = await followUpperBound();
		if(success == null) return false;
		console.clear();
		if(!success) {
			failedAttempts++;
			if(failedAttempts >= UPPER_BOUND_FOLLOW_RETRIES) {
				data.latestUpperBoundFollow -= UPPER_BOUND_FOLLOW_RETRIES;
				return true;
			}
		}
	}
	return true;
}

async function followUpperBound() {
	const data = new Data();
	console.log("Starting followUpperBound");
	const userId = data.latestUpperBoundFollow;
	while(true) {
		const error = await follow(userId);
		if(error == ErrorType.UNAUTHORIZED) {
			return null;
		}
		if(error == ErrorType.RATE_LIMITED) {
			console.log("Rate limited, waiting 15s");
			await sleep(15000);
			continue;
		}
		data.latestUpperBoundFollow += 1;
		if(error == null) {
			console.log("Follow success");
			break;
		}
		if(error == ErrorType.USER_NOT_FOUND) {
			console.log(`User ${userId} not found`);
			return false;
		}
		return false;
	}
	return true;
}
async function followLowerBound() {
	const data = new Data();
	console.log("Starting followLowerBound");
	const userId = data.latestLowerBoundFollow;
	while(true) {
		const error = await follow(userId);
		if(error == ErrorType.UNAUTHORIZED) {
			return null;
		}
		if(error == ErrorType.RATE_LIMITED) {
			console.log("Rate limited, waiting 15s");
			await sleep(15000);
			continue;
		}
		data.latestLowerBoundFollow += 1;
		if(error == null) {
			console.log("Follow success");
			return false;
		}
		if(error == ErrorType.USER_NOT_FOUND) {
			console.log(`User ${userId} not found`);
			return true;
		}
		return false;
	}
}


function getErrorType(jsonReponse) {
	if(!jsonReponse.hasOwnProperty("errors") || jsonReponse.errors.length == 0) {
		return null;
	}
	if(jsonReponse.errors.hasOwnProperty("userId")) return ErrorType.USER_NOT_FOUND;
	if(jsonReponse.hasOwnProperty("status") && jsonReponse.status == 429) return ErrorType.RATE_LIMITED;
	if(JSON.stringify(jsonReponse).includes("INTERNAL_ERROR")) return ErrorType.USER_NOT_FOUND;
	return ErrorType.UNKNOWN;
}

async function follow(userId) {
	console.log("Attempting to follower user ", userId);
	try {
		const response = await fetch(`https://api2.sololearn.com/v2/userinfo/v3/profile/follow/${userId}`, {
		  "headers": {
		    "accept": "application/json, text/plain, */*",
		    "accept-language": "en-GB,en;q=0.7",
		    "authorization": "Bearer "+getAccessToken(),
		    "cache-control": "no-cache",
		    "content-type": "application/json",
		    "pragma": "no-cache",
		    "priority": "u=1, i",
		    "sec-ch-ua": "\"Brave\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
		    "sec-ch-ua-mobile": "?0",
		    "sec-ch-ua-platform": "\"Windows\"",
		    "sec-fetch-dest": "empty",
		    "sec-fetch-mode": "cors",
		    "sec-fetch-site": "same-site",
		    "sec-gpc": "1",
		    "sl-locale": "en",
		    "sl-plan-id": "1",
		    "sl-time-zone": "+1"
		  },
		  "referrer": "https://www.sololearn.com/",
		  "body": "null",
		  "method": "POST",
		  "mode": "cors",
		  "credentials": "include"
		});
		// console.log(response);
		const json = await response.json();
		return getErrorType(json);
	} catch(e) {
		console.log(e);
		return ErrorType.UNAUTHORIZED;
	}
}

function checkTokenRefresh() {
  // For first time run, save the refreshToken
  if(!localStorage.getItem("refreshToken")) {
      localStorage.setItem("refreshToken", REFRESH_TOKEN);
      console.log("Saved your refresh token in the localStorage");
  }
  // Defaults to 0
	const expiresAt = 3600 + new Number((localStorage.getItem("lastTokenRefresh") ?? (getSeconds() - 3600)));
	const secondsTill = expiresAt - getSeconds();
	const secondsTillRefresh = secondsTill - 10*60; // Padding/Margin
	console.log(expiresAt, secondsTill)
	console.log(`Time till token refresh: ${secondsTillRefresh}`);
	if(secondsTillRefresh <= 10) return tokenRefresh();
	setTimeout(tokenRefresh, secondsTillRefresh*1000);
}
async function tokenRefresh() {
	const response = await fetch("https://api2.sololearn.com/v2/authentication/token:refresh", {
	  "headers": {
	    "accept": "application/json, text/plain, */*",
	    "accept-language": "en-GB,en;q=0.7",
	    "cache-control": "no-cache",
	    "content-type": "application/json",
	    "pragma": "no-cache",
	    "priority": "u=1, i",
	    "sec-ch-ua": "\"Brave\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
	    "sec-ch-ua-mobile": "?0",
	    "sec-ch-ua-platform": "\"Windows\"",
	    "sec-fetch-dest": "empty",
	    "sec-fetch-mode": "cors",
	    "sec-fetch-site": "same-site",
	    "sec-gpc": "1"
	  },
	  "referrer": "https://www.sololearn.com/",
	  "body": `\"${getRefreshToken()}\"`,
	  "method": "POST",
	  "mode": "cors",
	  "credentials": "omit"
	});
	const json = await response.json();
	localStorage.setItem("accessToken", json.accessToken);
	localStorage.setItem("refreshToken", json.refreshToken);
	localStorage.setItem("lastTokenRefresh", getSeconds());
	checkTokenRefresh();
}

function getRefreshToken() {
	return localStorage.getItem("refreshToken");
}

function getAccessToken() {
	return localStorage.getItem("accessToken");
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
