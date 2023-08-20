document.addEventListener('DOMContentLoaded', function() {

    // get all posts on page and update like count
    var doc = document.querySelectorAll(".post");
    for (var i = 0; i < doc.length; i++) {   
        var id = doc[i].id;
        var likeCountEle = doc[i].querySelector(".like-count");
        var likeButtonEle = doc[i].querySelector(".like-btn");
        getLikeCount(id, likeCountEle, likeButtonEle);
    };
  });
  
function getLikeCount(post_id, likeCountEle, likeButtonEle){
    fetch(`/likeCount/${ post_id }`)
    .then(response => response.json())
    .then(likes => {
        const likeCount = likes["count"];
        const reaction = likes["reaction"];
        const isAuthenticated = likes["isAuthenticated"];

        console.log(reaction);
        console.log(likeCount);

        // Populate like count
        likeCountEle.innerHTML = `${ likeCount.length } Like(s)`;

        // need to change button if user is authenticated
        if (isAuthenticated){
            likeCountEle.id = `like-btn-${ post_id }`;

            // activate like button colour depending on reaction (i.e True = user liked the post)
            if (reaction){
                likeButtonEle.innerHTML = "Unlike";
            } else{
                likeButtonEle.innerHTML = "Like";
            };
        };
    })
    // Catch any errors and log them to the console
    .catch(error => {
        console.log('Error:', error);
        likeCountEle.innerHTML = '0 Like(s)';
    });
    
    return false;
}

function updateLike(post_id){
    // get element based on id
    var doc = document.getElementById(`${ post_id }`)
    var likeCountEle = doc.querySelector(".like-count");
    var likeButtonEle = doc.querySelector(".like-btn");

    const reaction = likeButtonEle.innerHTML;

    // send out data
    fetch(`/updateLike`, {
        method: 'POST',
        headers:{'Content-Type': 'application/json'},
        body: JSON.stringify({
            postId: post_id,
            method: reaction,
        })
    })
    .then(response => response.json())
    .then(result => {
        // Print result
        console.log(result);
        getLikeCount(post_id, likeCountEle, likeButtonEle);
    })
    // Catch any errors and log them to the console
    .catch(error => {
        console.log('Error:', error);
    });

    return false;
}

function editPost(post_id){
    // get element based on id/ class
    var doc = document.getElementById(`${ post_id }`);
    var editEle = doc.querySelector(".edit-content");
    var editAreaEle = editEle.querySelector("textarea");

    // unhide edit pane
    unhideEditPane(post_id, true);

    // update text
    editAreaEle.value = contentEle.textContent.trim();

    return false;
}

function updatePost(post_id, trigger){
    // get element based on id/ class
    var doc = document.getElementById(`${ post_id }`);
    var contentEle = doc.querySelector(".content");
    var editEle = doc.querySelector(".edit-content");
    var editAreaEle = editEle.querySelector("textarea");

    // reset to default layout if trigger is false
    if (!trigger){
        // hide edit pane
        unhideEditPane(post_id, false);
    } else{
        const content = editAreaEle.value.trim();
        const errorFlag = false;

        fetch(`/updatePost`, {
            method: 'PUT',
            headers:{'Content-Type': 'application/json'},
            body: JSON.stringify({
                postId: post_id,
                content: content,
            })
        })
        .then(response => response.json())
        .then(result => {
            // Print result
            console.log(result);

            if ("Success" in result){
                // hide edit pane
                unhideEditPane(post_id, false);
                // update text
                contentEle.innerHTML = content;
            } else{
                alert(result.error);
            };
        })
        // Catch any errors and log them to the console
        .catch(error => {
            console.log('Error:', error);
        });       
    };

    return false;
}

function followUser(trigger, profileName){
    // send out data
    fetch(`/followUser`, {
        method: 'POST',
        headers:{'Content-Type': 'application/json'},
        body: JSON.stringify({
            trigger: trigger,
            profile: profileName,
        })
    })
    .then(response => response.json())
    .then(result => {
        // Print result
        console.log(result);

        if ("Success" in result){
            var followBtn = document.querySelector(".follow-btn");
            var unfollowBtn = document.querySelector(".unfollow-btn");
            var followerCountEle = document.querySelector(".followers");
            
            if (trigger){
                followBtn.style.display = "none";
                unfollowBtn.style.display = "block";
            } else{
                followBtn.style.display = "block";
                unfollowBtn.style.display = "none";
            };

            followerCountEle.innerHTML = `${result.followers.length} follower(s)`;
        } else{
            alert(result.error);
        };
    })
    // Catch any errors and log them to the console
    .catch(error => {
        console.log('Error:', error);
    });

    return false;
}

function unhideEditPane(post_id, unhide){
    // get element based on id/ class
    var doc = document.getElementById(`${ post_id }`);
    var contentEle = doc.querySelector(".content");
    var likeCountEle = doc.querySelector(".like-count");
    var stdButtonEle = doc.querySelector(".std-btns");
    var editEle = doc.querySelector(".edit-content");

    if (unhide){
        contentEle.style.display = 'none';
        likeCountEle.style.display = 'none';
        stdButtonEle.style.display = 'none';
        editEle.style.display = 'block';
    } else{
        contentEle.style.display = 'block';
        likeCountEle.style.display = 'block';
        stdButtonEle.style.display = 'block';
        editEle.style.display = 'none';
    };
}