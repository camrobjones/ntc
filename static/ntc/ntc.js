

// Compass helper funcs
function roundTo(num, dp) {
    dp = dp || 2;
    let mult = 10 ** dp;
    return Math.round(num * mult) / mult;
}

function miniMax(num, min, max) {
    num = Math.min(num, max);
    num = Math.max(num,  min);
    return num;
}

// Check URL valid
function validURL(str) {
  var pattern = new RegExp('^(https?:\\/\\/)?'+ // protocol
    '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|'+ // domain name
    '((\\d{1,3}\\.){3}\\d{1,3}))'+ // OR ip (v4) address
    '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*'+ // port and path
    '(\\?[;&a-z\\d%_.~+=-]*)?'+ // query string
    '(\\#[-a-z\\d_]*)?$','i'); // fragment locator
  return !!pattern.test(str);
}

function searchTopic() {
    let url = "/pointthecompass/search_topic";
    let csrftoken = Cookies.get('csrftoken');
    let headers = {'X-CSRFToken': csrftoken};
    let data = {
            "query": "liber"
             };
    axios.post(url,data,{headers: headers})
        .then(response => {
            console.log(response);
        });
}

const cat2icon = {
    "PER": "person",
    "POL": "description",
    "GOV": "account_balance",
    "COU": "public",
    "WOR": "menu_book",
    "PHI": "emoji_objects",
    "OTH": "more_horiz"
};

const cat2name = {
    "PER": "Person",
    "POL": "Policy",
    "GOV": "Government",
    "COU": "Country",
    "WOR": "Work",
    "PHI": "Philosophy",
    "OTH": "Other"
};

function buildVegaSpec(data) {
    let spec = {
      "$schema": "https://vega.github.io/schema/vega/v5.json",
      "width": 600,
      "height": 600,
      "padding": 5,
      "data": [
        {
          "name": "source",
          "values": data,
          "transform": [
            {
              "type": "filter",
              "expr": "datum['topic_name'] != null && datum['x'] != null && datum['y'] != null"
            }
          ]
        }
      ],
      "signals": [
          {
          "name": "width",
          "value": "600",
          "on": [
            {
              "events": {
                "source": "window",
                "type": "resize"
              },
              "update": "containerSize()[0]"
            },
            {
              "events": {
                "source": "window",
                "type": "load"
              },
              "update": "containerSize()[0]"
            }
          ]
        },
        {
          "name": "height",
          "value": "600",
          "on": [
            {
              "events": {
                "source": "window",
                "type": "resize"
              },
              "update": "containerSize()[1]"
            },
            {
              "events": {
                "source": "window",
                "type": "load"
              },
              "update": "containerSize()[0]"
            }
          ]
        }
      ],
      "scales": [
        {
          "name": "x",
          "type": "linear",
          "round": true,
          "nice": true,
          "zero": true,
          "domain": {"data": "source", "field": "x"},
          "domainMin": -10,
          "domainMax": 10,
          "range": "width"
        },
        {
          "name": "y",
          "type": "linear",
          "round": true,
          "nice": true,
          "zero": true,
          "domainMin": -10,
          "domainMax": 10,
          "domain": {"data": "source", "field": "y"},
          "range": "height"
        }
      ],
      "axes": [
        {
          "scale": "x",
          "grid": false,
          "domain": false,
          "labels": false,
          "ticks": false,
          "offset": 0,
          "orient": "bottom"
        },
        {
          "scale": "y",
          "grid": false,
          "domain": false,
          "labels": false,
          "ticks": false,
          "offset": 0,
          "orient": "left"
        }
      ],
      "legends": [
      ],
      "marks": [
        {
          "name": "points",
          "clip": true,
          "type": "symbol",
          "from": {"data": "source"},
          "interactive": true,
          "hover": {},
          "encode": {
            "enter": {
              "x": {"scale": "x", "field": "x"},
              "y": {"scale": "y", "field": "y"},
              "shape": {"value": "circle"},
              "strokeWidth": {"value": 1},
              "size": {"signal": "width / 10"},
              "opacity": {"value": 0.8},
              "stroke": {"value": "black"},
              "fill": {"value": "red"},
              "href": {"signal": "'/pointthecompass/vote/' + datum.topic_id"},
              "tooltip": {"signal": "{'Topic': datum.topic_name, 'Category': datum.category}"},
              "cursor": {"value": "pointer"}
            },
            "update": {
              "x": {"scale": "x", "field": "x"},
              "y": {"scale": "y", "field": "y"},
              "shape": {"value": "circle"},
              "strokeWidth": {"value": 1},
              "size": {"signal": "width / 10"},
              "opacity": {"value": 0.8},
              "stroke": {"value": "black"},
              "fill": {"value": "red"}
            }
          }
        },
        { 
          "name": "topics",
          "type": "text",
          "clip": true,
          "from": {"data": "points"},
          "encode": {
            "enter": {
              "text": {"field": "datum.topic_name"},
              "fontSize": {"signal": "width / 35"},
            },
            "update": {
              "text": {"field": "datum.topic_name"},
              "fontSize": {"signal": "width / 35"}
            },
          },
          "transform": [
            {
              "type": "label",
              "avoidMarks": ["points"],
              "offset": [1],
              "size": {"signal": "[width, height]"}
            }
          ]
        }
      ],
      "config": {}
    }

    return spec;
}

// Data Templates

function createTemplate() {
    let data = {
                active: false,
                valid: false,
                name: "",
                description:"",
                category: "",
                url: "",
                errors: {
                    name: "",
                    description: "",
                    category: "",
                    url: ""
                },
                similar: {
                    topics: [],
                    message: ""
                },
            };
    return data;
}


function defaultUser() {
    let user = {
        username: "Guest User",
        is_authenticated: false,
        guest: true,
        image_url: '/static/spyke/images/guest.jpg',
        stats: {}
    };
    return user;
}

function defaultUserMenu() {
    let userMenu = {
            open: false,
            mode: "signup",
            login: {
                username: "",
                password: "",
                error: "",
            },
            signup: {
                username: "",
                email: "",
                password: "",
                passwordConfirm: "",
                errors: [],
            }
        };
    return userMenu;
}


// Vue Directives

Vue.directive('click-outside', {
  bind: function (el, binding, vnode) {
    el.clickOutsideEvent = function (event) {
      // here I check that click was outside the el and his children
      if (!(el == event.target || el.contains(event.target))) {
        // and if it did, call method provided in attribute value
        vnode.context[binding.expression](event);
      }
    };
    document.body.addEventListener('click', el.clickOutsideEvent);
  },
  unbind: function (el) {
    document.body.removeEventListener('click', el.clickOutsideEvent);
  },
});

// Vue Setup

Vue.config.delimiters = ["[[", "]]"];

var app = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    mounted: function() {

        console.log("mounted");

        // Get user

        // Retrieve topic data
        user = document.getElementById('user');
        if (user) {
            this.user = JSON.parse(user.textContent);
            if (this.user.is_authenticated & this.user.guest == false) {
                this.userMenu.mode = "profile";
                this.setUserDates();
            }
        }

        this.axiosSetup();

        // Retrieve topic data
        topicEl = document.getElementById('topic');
        if(topicEl) {
            this.page = "vote";
            topic = JSON.parse(topicEl.textContent);
            if (Object.keys(topic).length > 0) {
                this.topic = topic;

                // Check if user has voted
                if ("info" in topic &&
                    "user_vote" in topic.info &&
                    topic.info.user_vote != null &&
                    "x" in topic.info.user_vote) {
                    this.mode = "review";
                    this.vote = topic.info.user_vote;
                }

            } else {
                this.nextTopic();
            }
        }

        // Get topics (home)
        topics = document.getElementById('topics');
        if (topics) {
            this.topics = JSON.parse(topics.textContent);
        }

        // Compass setup
        console.log(this.topics);
        this.drawCompassCoords(this.topics, '#vis-home');
    },
    data: {
        // General
        page: "home",
        mode: "vote",
        modal: "",

        // Home
        topics: [],

        // Vote
        topic: {},
        topicInfo: false,
        instructions: false,
        votes: [],
        vote: {
            x: 0,
            y: 0
        },
        
        // Profile
        profile: {},
        user: defaultUser(),
        userMenu: defaultUserMenu(),

        // Compass
        compass: {
            dragging: false
        },

        // Search
        search: 
            {
                query: "",
                results: [],
                send_time: 0,
                timer: null,
                searches: [],
            },

        // Create
        create: createTemplate(),

        // Notifications
        notification: {
            labelText: "",
            actionButtonText: "",
            type: "",
        }
    },
    computed: {
    },
    methods: {

        // == Setup ==

        // MDC
        setupMDC: function() {
            // MDC Elements
            this.topAppBarElement = document.querySelector('.mdc-top-app-bar');
            this.topAppBar = new mdc.topAppBar.MDCTopAppBar(this.topAppBarElement);

            // Snackbar
            this.snackbar = new mdc.snackbar.MDCSnackbar(document.querySelector('.mdc-snackbar'));

            // Dialog
            this.outOfTopics = new mdc.dialog.MDCDialog(document.querySelector('.mdc-dialog'));
        },

        // Axios
        axiosSetup() {
            // Get csrf token
            let csrftoken = Cookies.get('csrftoken');
            let headers = {'X-CSRFToken': csrftoken};

            // Create axios instance
            this.axios = axios.create({
                headers: headers
            });

            // axios response interceptor
            this.axios.interceptors.response.use(function (response) {
                
                let data = response.data;

                if (!data.success && !data.handled) {
                    // Notify lack of success
                    let message = data.error || `Request to ${response.config.url} failed...`;
                    app.notify(message, "Okay", "error");

                    // Return response anyway
                    return response;
                } else {
                    // Return response as normal
                    return response;
                }
                
              }, function (error) {
                // Notify function failure
                let message = `Request to ${error.config.url} failed...`;
                app.notify(message, "Okay", "error");
                return false;
              });
        },

        /* == Compass == */

        drawCompassCoords: function(data, elId) {
            // Draw compass co-ords
            const spec = buildVegaSpec(data);
            vegaEmbed(elId, spec, {"actions": false})
              // result.view provides access to the Vega View API
              .then(result => console.log(result))
              .catch(console.warn);
        },

        // Find values on the compass
        valueToCoord: function(val) {
            let prop = ((val + 10) / 20);
            return (prop * 100) + '%';
        },

        // Left or right align label?
        getTextAnchor: function(xval) {
            if (xval > 5) {
                return "end";
            } else {
                return "start";
            }
        },

        // Get x offset
        getLabelDx: function(xval) {
            if (xval > 5) {
                return "-5px";
            } else {
                return "5px";
            }
        },

        // Map categories to icons
        get_cat_icon: function(cat) {
            return cat2icon[cat];
        },

        // Map categories to names
        get_cat_name: function(cat) {
            return cat2name[cat];
        },

        // Get URL demo for topic links
        get_url_demo: function(url) {
            if (url != undefined) {
                let parts = url.split('/');
                let host = parts[2];
                return host;
            }
        },

        // Truncate text
        trunc: function(text, chars) {
            if (text.length < chars) {
                return text;
            }

            return text.substring(0, chars-3) + "...";
        },

        // Compass tracking
        updateCoords: function(evt) {
            if (this.mode != "vote") {
                return;
            }
            // Get the compass element
            var cmp = document.getElementById('compass');
            var dim = cmp.getBoundingClientRect();

            // Find x position
            var x = (evt.clientX - dim.left) / dim.width;
            x = (x - 0.5) * 20;
            x = roundTo(x, 2);
            x = miniMax(x, -10, 10);

            // Find y position
            var y = (evt.clientY - dim.top) / dim.height;
            y = (y - 0.5) * -20;
            y = roundTo(y, 2);
            y = miniMax(y, -10, 10);
            
            // update data
            this.vote.x = x;
            this.vote.y = y;
        },
        compassTouch: function(evt) {
            // Treat
            this.updateCoords(evt.changedTouches[0]);
        },
        compassMouseover: function(evt) {
            if (this.compass.dragging) {
                this.updateCoords(evt);
            }
        },
        compassMousedown: function(evt) {
            this.compass.dragging = true;
            this.updateCoords(evt);
        },
        compassMouseup: function(evt) {
            if (this.compass.dragging) {
                this.updateCoords(evt);
            }
            this.compass.dragging = false;
        },
        compassMouseoff: function(evt) {
            // this.compass.dragging = false;
        },

        /* == State Updating == */

        // Load new topic
        loadTopic: function(topic) {
            this.topic = topic;
            let html = document.getElementsByTagName("html").innerHTML;
            let urlPath = "/pointthecompass/vote/" + topic.id + "/";
            window.history.replaceState({"html":html, "pageTitle":document.title},"", urlPath);
            if (topic.info.user_vote != null) {
                this.vote = topic.info.user_vote;
                this.mode = "review";
            } else {
                this.vote = {"x": 0, "y": 0};
                this.mode = "vote";
            }
                this.modal = "";
        },

        toggleTopicInfo: function(topic) {
            this.topicInfo = !this.topicInfo;
            this.instructions = false;
        },

        toggleInstructions: function(topic) {
            this.instructions = !this.instructions;
            this.topicInfo = false;
        },

        closeInfoPopups: function() {
            if (this.instructions) {
                this.instructions = false;
            }
            if (this.topicInfo) {
                this.topicInfo = false;
            }
        },

        // Get next topic
        nextTopic: function() {
            // Async update if user is already voting
            if (this.page == "vote") {
                let url = "/pointthecompass/next_topic/";
                this.axios.get(url)
                    .then(response => {
                        if (response && response.data) {

                            if (response.data.success) {
                                this.loadTopic(response.data.topic);
                            } else {
                                // Handle Out of topic Error

                                // Load last voted topic
                                let data = response.data;
                                this.mode = "review";
                                this.topic = data.topic;
                                this.vote = data.topic.info.user_vote;

                                this.setupMDC(); // Ensure MDC modal is loaded
                                console.log(this.outOfTopics);
                                Vue.nextTick(function() {
                                    app.outOfTopics.open();
                                });
                                
                                this.$forceUpdate();
                            }

                            
                        }
                    });
            } else {
                // Redirect if user is home
                window.location.href = "/pointthecompass/vote/";
            }
        },

        // Get next topic
        getTopic: function(topic_id) {
            // Async update if user is already voting
            if (this.page == "vote") {
                let url = `/pointthecompass/get_topic/${topic_id}/`;
                this.axios.get(url)
                    .then(response => {
                        if (response && response.data) {
                            console.log(response);
                            this.loadTopic(response.data.topic);
                        }
                });
            } else {
                window.location.href = `/pointthecompass/vote/${topic_id}/`;
            }
        },

        // Get random topic
        randomTopic: function() {
            let url = `/pointthecompass/random_topic/`;
            this.axios.get(url)
                .then(response => {
                    if (response && response.data) {
                        this.loadTopic(response.data.topic);
                    }
            });
        },
        
        // Submit vote
        submitVote: function() {
            let url = "/pointthecompass/submit_vote/";
            let data = {
                    "topic_id": this.topic.id,
                    "x": this.vote.x,
                    "y": this.vote.y,
                     };

            this.axios.post(url,data)
                .then(response => {
                    if (!response && !response.data) {return;}
                    
                    let data = response.data;
                    this.mode = "review";
                    this.topic = data.topic;
                    this.vote = data.topic.info.user_vote;

                    // Focus Next
                    setTimeout(function(){
                        document.getElementById("next-btn").focus();
                    }, 100);
                });
        },

        // Submit vote
        skipTopic: function() {
            let url = "/pointthecompass/skip_topic/";
            let data = {
                    "topic_id": this.topic.id};

            this.axios.post(url,data)
                .then(response => {
                    if (response && response.data) {
                        this.loadTopic(response.data.topic);
                    }
                });
        },

        voteEnter: function() {
            // shortcut to advance
            if (this.mode == "vote") {
                this.submitVote();
            } else {
                this.nextTopic();
            }
        },

        // toggle Modals
        toggleSearch: function(mode) {
            if (this.modal == "search") {
                this.modal = "";
            } else {
                this.modal = "search";
                setTimeout(function(){
                    document.getElementById("searchbar").focus();
                }, 100);
            }
        },
        
        toggleCreate: function(mode) {
            if (this.modal == "create") {
                this.modal = "";
            } else {
                this.modal = "create";
            }
        },

        toggleAuth: function(mode) {
            if (this.modal == "auth") {
                this.modal = "";
            } else {
                this.modal = "auth";
                this.getUserData();
                Vue.nextTick(function(){
                    app.drawCompassCoords(app.user.votes, '#vis-user');
                });
            }
        },

        // Search
        clearSearchTimer: function() {
            clearTimeout(this.search.timer);
        },

        setSearchTimer: function() {
            // trigger search 400ms after typing stops;
            let searchTimeout = 400;

            // clear timer
            clearTimeout(this.search.timer);
            this.search.timer = setTimeout(
                this.searchQuery, searchTimeout
            );

        },

        checkTopicDuplicates: function () {
            let url = "/pointthecompass/check_topic_duplicates/";
            let csrftoken = Cookies.get('csrftoken');
            let headers = {'X-CSRFToken': csrftoken};
            let data = {"queries":
                {
                    "name_score": {"fields": "name", "term": this.create.name},
                    "description_score": {"fields": "description", "term": this.create.description},
                    "category_score": {"fields": "category", "term": this.create.category},
                    "url_score": {"fields": "url", "term":  this.create.url}
                }
                };
            console.log(data);
            axios.post(url,data,{headers: headers})
                .then(response => {
                    console.log(response);
                    let data = response.data;
                    // If there are similar topics
                    if (data.count > 0) {
                        this.create.similar.topics = data.topics;
                        this.create.similar.message = data.message;
                    } else {
                        this.create.similar.topics = [];
                        this.create.similar.message = "";
                    }
                });
        },

        searchQuery: function() {
            // Make a copy of the search string
            let query = this.search.query;

            // Cancel if same search is ongoing
            if (query in this.search.searches) {
                return;
            }
            // Add query to searches
            this.search.searches.push(query);

            // Create URL and params
            let url = "/pointthecompass/search_topic";
            let params = {"query": query};

            // Make API Call
            this.axios.get(url,{params: params})
                .then(response => {
                    if (response && response.data) {
                        let data = response.data;
                        console.log(data.results);
                        this.storeSearchResults(data.results);

                        // Remove query from searches array
                        let searchesIndex = this.search.searches
                            .indexOf(query);
                        this.search.searches.splice(searchesIndex, 1);
                    } else {
                        this.search.searches = [];
                    }

                    
                });
        },

        storeSearchResults: function(results) {
            // Store new search results
            this.search.results = results;
        },

        // Create
        validateName: function() {
            let name = this.create.name;
            if (name.length < 1) {
                this.create.errors.name = ["Name must contain at least 1 character."];
                return ;
            }
            if (name.length > 50) {
                this.create.errors.name = ["Name must contain fewer than 50 characters."];
                return;
            }
            this.create.errors.name = "";
            this.checkTopicDuplicates();
        },

        validateDescription: function() {
            let description = this.create.description;
            if (description.length > 1000) {
                this.create.errors.description = ["Description must contain fewer than 1000 characters."];
                return;
            }
            this.create.errors.description = "";
            this.checkTopicDuplicates();
        },

        validateCategory: function() {
            let cat = this.create.category;
            if (!(cat in cat2icon)) {
                this.create.errors.category = ["Please select a category."];
                return;
            }
            this.create.errors.category = "";
        },

        validateURL: function() {
            let url = this.create.url;
            if (url != "" && !(validURL(url))) {
                this.create.errors.url = ["That URL is not valid."];
                return;
            }
            this.create.errors.url = "";
            this.checkTopicDuplicates();
        },

        validateCreate: function() {
            this.validateName();
            this.validateDescription();
            this.validateCategory();
            this.validateURL();
            this.checkTopicDuplicates();
            let valid = !Object.values(this.create.errors).some(x=>x);
            this.create.valid = valid;
            return valid;
        },

        submitCreate: function() {
            let valid = this.validateCreate;
            if (valid) {
                this.createTopic();
            }
        },

        clearCreate: function() {
            this.create = createTemplate();
            this.modal = "";
        },

        createTopic: function() {
            let url = "/pointthecompass/create_topic/";
            let csrftoken = Cookies.get('csrftoken');
            let headers = {'X-CSRFToken': csrftoken};
            let data = {
                    "name": this.create.name,
                    "description": this.create.description,
                    "category": this.create.category,
                    "url": this.create.url
                     };
            axios.post(url,data,{headers: headers})
                .then(response => {
                    console.log(response);
                    let data = response.data;

                    // Reset local errors 
                    this.create.errors = {};

                    // Handle errors
                    if (!data.success) {

                        if (data.errors) {
                            this.create.errors = data.errors;
                        }
                        
                        return;
                    }
                    this.clearCreate();
                    this.loadTopic(data.topic);
                    this.notify(`The topic "${data.topic.name} was created.`,
                                 "Okay", "success");

                });
        },

        notify: function(labelText, actionButtonText, type) {
            this.notification = {
                "labelText": labelText || "",
                "actionButtonText": actionButtonText || "Okay",
                "type": type || ""
                };
            this.snackbar.open();
        },

        // === User Stuff ====

        getUser: function(response) {
            let user = response.data.user;
            if (user.is_authenticated) {
                    this.user = response.data.user;
                    this.setUserDates();
                  }
        },

        getUserData: function() {
            let url = '/pointthecompass/get_user_data/';
            let csrftoken = Cookies.get('csrftoken');
            let headers = {'X-CSRFToken': csrftoken};
            axios.get(url,{},{headers: headers})
              .then(response => {
                  console.log(response.data);
                  if (response.data.success) {
                    this.getUser(response);

                    // Update user compasss
                    if (this.modal=="auth") {
                        app.drawCompassCoords(app.user.votes, '#vis-user');
                    }
                } else {
                    this.userMenu.signup.errors = response.data.errors;
                    this.notify(message,
                                 "Okay", "error");
                    this.$forceUpdate();
                }
                  
            });
        },

        setUserDates: function() {
        // Transform dates
                let created = new Date(this.user.created);
                this.user.created = created.toLocaleDateString();

                let lastActive = new Date(this.user.last_active);
                this.user.last_active = lastActive.toLocaleDateString();
            },

        openUserMenu: function(mode){
            let modes = ["login", "signup", "profile"];
            if (modes.includes(mode)) {
                this.userMenu.mode = mode;
            } else {
                if (this.user.is_authenticated & this.user.guest == false) {
                    this.userMenu.mode = "profile";
                } else {
                    this.userMenu.mode = "signup";
                }
            }
            this.userMenu.open = true;
            // document.getElementById('main-container')
            //     .addEventListener('click', function(e) {
            //         app.dismissModals();
            //     }, { once: true });
            },

        loginUser: function() {
            let url = '/pointthecompass/login_user/';
            let csrftoken = Cookies.get('csrftoken');
            let headers = {'X-CSRFToken': csrftoken};
            let data = this.userMenu.login;
            axios.post(url,data,{headers: headers})
              .then(response => {
                  console.log(response.data);
                  if (response.data.success) {
                    this.getUser(response);
                    this.modal = "";
                    this.userMenu.mode = "profile";
                    this.userMenu.login.error = "";
                    this.notify(`Welcome back, ${app.user.username}!`,
                                 "Okay", "success");
                } else {
                    this.userMenu.login.error = response.data.message;
                    this.$forceUpdate();
                }
                  
            });
        },

        logout: function() {
            let url = '/pointthecompass/logout/'
            let csrftoken = Cookies.get('csrftoken');
            let headers = {'X-CSRFToken': csrftoken};
            axios.get(url,{headers: headers})
              .then(response => {
                  console.log(response.data);
                  if (response.data.success) {
                    this.user = defaultUser();
                    this.userMenu = defaultUserMenu();
                    this.modal = "";
                    window.location.href = "/pointthecompass/";
                    this.notify("You have been logged out", "Okay",
                        "success.");
                } else {
                    console.log("Logout failed");
                    this.notify("Logout failed: try again in a few seconds.",
                                  "Okay", "error");
                }
                  
            });
        },

        signup: function() {
            let url = '/pointthecompass/signup/';
            let csrftoken = Cookies.get('csrftoken');
            let headers = {'X-CSRFToken': csrftoken};
            let data = this.userMenu.signup;
            axios.post(url,data,{headers: headers})
              .then(response => {
                  console.log(response.data);
                  if (response.data.success) {
                    this.getUser(response);
                    this.modal = "";
                    this.userMenu.mode = "profile";
                    this.userMenu.signup.errors = [];
                    this.notify(`Thanks for signing up, ${app.user.username}!`,
                                 "Okay", "success");
                } else {
                    this.userMenu.signup.errors = response.data.errors;
                    this.$forceUpdate();
                }
                  
            });
        },

        requestLogin: function() {
            // Notify user that they need to login and open signup panel
            this.notify("Please signup or login", "Okay", "error");
            this.toggleAuth();

        },

        enforceLogin: function() {
            // Check user is logged in and requestLogin if not
            if (this.user.is_authenticated) {
                return true;
            } else {
                this.requestLogin();
                return false;
            }
        },
    }
});

// Vue components

Vue.component('ntc-comment', {
    props: ["profile", "text", "score"],
    template: `<div class='comment'>
                <div class='comment-header'>
                    <span class='score' v-html="score"></span>
                </div>
                <div class='comment-body' v-html='text'>
                </div>
               </div>`
});

window.addEventListener("load", function(){
    app.setupMDC();

});
