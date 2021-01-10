

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
    let url = "/ntc/search_topic";
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

// Vue Setup

Vue.config.delimiters = ["[[", "]]"];

var app = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    mounted: function() {

        this.axiosSetup();

        // Retrieve topic data
        topic = JSON.parse(document.getElementById('topic').textContent);
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
    },
    data: {
        topic: {},
        votes: [],
        vote: {
            x: 0,
            y: 0
        },
        mode: "vote",
        modal: "",
        profile: {},
        compass: {
            dragging: false
        },
        search: 
            {
                query: "",
                results: [],
                send_time: 0,
                timer: null,
                searches: [],
            },
        create: createTemplate(),
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

                if (!data.success) {
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

        // Find values on the compass
        valueToCoord: function(val) {
            let prop = ((val + 10) / 20);
            return (prop * 100) + '%';
        },

        // Map categories to icons
        get_cat_icon: function(cat) {
            return cat2icon[cat];
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
            this.compass.dragging = false;
            this.updateCoords(evt);
        },
        compassMouseoff: function(evt) {
            this.compass.dragging = false;
        },

        /* == State Updating == */

        // Load new topic
        loadTopic: function(topic) {
            this.topic = topic;
            this.vote = {"x": 0, "y": 0};
            this.mode = "vote";
            this.modal = "";
        },


        // Get next topic
        nextTopic: function() {
            let url = "/ntc/next_topic/";
            this.axios.get(url)
                .then(response => {
                    if (response && response.data) {
                        this.loadTopic(response.data.topic);
                    }
            });
        },

        // Get next topic
        getTopic: function(topic_id) {
            let url = `/ntc/get_topic/${topic_id}/`;
            this.axios.get(url)
                .then(response => {
                    if (response && response.data) {
                        this.loadTopic(response.data.topic);
                    }
            });
        },

        // Get random topic
        randomTopic: function() {
            let url = `/ntc/random_topic/`;
            this.axios.get(url)
                .then(response => {
                    if (response && response.data) {
                        this.loadTopic(response.data.topic);
                    }
            });
        },
        
        // Submit vote
        submitVote: function() {
            let url = "/ntc/submit_vote/";
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
                });
        },

        // toggle Modals
        toggleSearch: function(mode) {
            if (this.modal == "search") {
                this.modal = "";
            } else {
                this.modal = "search";
            }
        },
        toggleCreate: function(mode) {
            if (this.modal == "create") {
                this.modal = "";
            } else {
                this.modal = "create";
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
            let url = "/ntc/check_topic_duplicates/";
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
            let url = "/ntc/search_topic";
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
                this.create.errors.name = "Name must contain at least 1 character.";
                return ;
            }
            if (name.length > 50) {
                this.create.errors.name = "Name must contain fewer than 50 characters.";
                return;
            }
            this.create.errors.name = "";
            this.checkTopicDuplicates();
        },

        validateDescription: function() {
            let description = this.create.description;
            if (description.length > 1000) {
                this.create.errors.description = "Description must contain fewer than 1000 characters.";
                return;
            }
            this.create.errors.description = "";
            this.checkTopicDuplicates();
        },

        validateCategory: function() {
            let cat = this.create.category;
            if (!(cat in cat2icon)) {
                this.create.errors.category = "Please select a category.";
                return;
            }
            this.create.errors.category = "";
        },

        validateURL: function() {
            let url = this.create.url;
            if (url != "" && !(validURL(url))) {
                this.create.errors.url = "That URL is not valid.";
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
            let url = "/ntc/create_topic/";
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
