import Vue from 'vue';

window.onload = function () {
    let player = new Vue({
        el: '#player',
        data: {
            title: '',
            artist: '',
            album: '',
            length: '',
            playlist: [],
            playing: false,
            progress: 0
        },
        methods: {
            playNext: function () {
                let request = new Request('/next');
                fetch(request);
                this.updateTrackInfo();
            },
            playPrev: function () {
                let request = new Request('/prev');
                fetch(request);
                this.updateTrackInfo();
            },
            playPause: function () {
                let request = new Request('/toggle_play');
                fetch(request);
                this.updateState();
            },
            stop: function () {
                let request = new Request('/stop');
                fetch(request);
                this.updateTrackInfo();
                this.updateState();
            },
            volumeUp: function () {
                let request = new Request('/volume_up');
                fetch(request);
            },
            volumeDown: function () {
                let request = new Request('/volume_down');
                fetch(request);
            },
            updateTrackInfo: function () {
                let request = new Request('/get_track_info');
                let that = this;

                fetch(request).then(function (response) {
                    return response.json();
                }).then(function (data) {
                    that.title = data['title'];
                    that.album = data['album'];
                    that.artist = data['artist'];
                });
            },
            updatePlaylist: function () {
                let request = new Request('/playlist');
                let that = this;

                fetch(request).then(function (response) {
                    return response.json();
                }).then(function (data) {
                    that.playlist = [];

                    for (let i = 0; i < data.length; ++i) {
                        that.playlist.push({
                            id: i,
                            title: data[i]['title'],
                            artist: data[i]['artist'],
                            length: data[i]['length']
                        });
                    }
                });
            },
            updateState: function () {
                let request = new Request('/get_state');
                let that = this;

                fetch(request).then(function (response) {
                    return response.json();
                }).then(function (data) {
                    that.playing = data['state'] === 'playing';
                    that.progress = data['progress'];
                });
            },
            jumpToTrack: function (index) {
                let current_index = 0;

                for (let i = 0; i < this.playlist.length; ++i) {
                    if ((this.playlist[i].title === this.title)
                        && (this.playlist[i].artist === this.artist)) {
                        current_index = i;
                        break;
                    }
                }

                let offset = index - current_index;

                if (offset > 0) {
                    this.playlistForward(offset);
                } else if (offset < 0) {
                    this.playlistBackward(offset);
                }
            },
            playlistForward: function (num) {
                let request = new Request('/playlist_go/' + num);
                let that = this;

                fetch(request).then(function () {
                    that.updateTrackInfo();
                });
            },
            playlistBackward: function (num) {
                let request = new Request('/playlist_go_back/' + (-num));
                let that = this;

                fetch(request).then(function () {
                    that.updateTrackInfo();
                });
            }
        },
        mounted: function () {
            let that = this;

            // At startup, update everything
            that.updateTrackInfo();
            that.updateState();
            that.updatePlaylist();

            setInterval(function () {
                that.updateState();
            }, 2000);

            setInterval(function () {
                that.updateTrackInfo();
            }, 5000);
        },
        watch: {
            title: function (oldTitle, newTitle) {
                if (oldTitle !== newTitle)
                    this.updatePlaylist();
            }
        }
    });
};
