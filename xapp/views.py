from xapp.application import app, lm
from xapp.forms import GroupForm, LoginForm, SignUpForm, BillForm, FriendForm
from xapp.groups import AddGroup, Group
from flask import request, redirect, render_template, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from xapp.models import USERS_COLLECTION, GROUPS_COLLECTION, BILLS_COLLECTION, TRANSACTION_COLLECTION
from xapp.user import User
from bson.objectid import ObjectId
from xapp.oauth import OAuthSignIn
import pymongo
import requests


@app.route('/', methods=['GET'])
@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = USERS_COLLECTION.find_one({"_id": form.username.data})
        if user and User.validate_login(user['password'], form.password.data):
            user_obj = User(user['_id'])
            login_user(user_obj, remember=True)
            flash("Logged in successfully!", category='success')
            return redirect(url_for('dashboard'))
        flash("Wrong username or password!", category='error')
    print(current_user.get_id())
    return render_template('login.html', title='DiviPay | Login', form=form)
# login1.html kara hai

'''
@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = USERS_COLLECTION.find_one({'email': form.email.data})
        if user:
            flash("You have already signed up from this email id", category='error')
        else:
            user = USERS_COLLECTION.find_one({'_id': form.username.data})
            if user:
                flash("That username has already been taken", category='error')
            else:
                User(form.username.data, form.email.data, form.firstname.data,
                        form.lastname.data, form.password.data, db=True)
                flash("SignUp successfull!", category='success')
                return redirect(url_for('login'))
    return render_template('signup.html', title='HoverSpace | Signup', form=form)
'''

@app.route('/dashboard/')
def dashboard():
    return "dashboard"
    #render_template('dashboard.html')


@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('dashboard'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('login'))
    oauth = OAuthSignIn.get_provider(provider)
    username, email = oauth.callback()
    if email is None:
        flash('Authentication failed.')
        return redirect(url_for('login'))
    user = USERS_COLLECTION.find_one({'_id': email})
    if not user:
        nick = username
        if nick is None or nick == "":
            nick = email.split('@')[0]
        user = User(email, nickname=nick, db=True)

    login_user(user, remember=True)
    print(current_user.get_id())
    return redirect(url_for('dashboard'))

@app.route('/addgroup/', methods=['GET', 'POST'])
def addGroup():
    userID = current_user.get_id()
    form = GroupForm()
    userFriends = (USERS_COLLECTION.find_one({'_id': userID}))['friends']
    if request.method == 'POST':
        group = AddGroup(form.name.data, request.form.getlist('friend'))
        groupID = group.addGroup()
        usr = User(userID)
        usr.updateGroups(groupID)
        return redirect(url_for('viewGroup', groupID=groupID))
    return render_template('create_group.html', form=form, friends=userFriends)


@app.route('/groups/<groupID>/', methods=['GET'])
def viewGroup(groupID):
    return render_template('group.html', groupID=groupID, title="DiviPay | Groups")


@app.route('/groups/<groupID>/simplify', methods=['GET'])
def simplification(groupID):
    grp = Group(groupID)
    grp.simplify()
    return redirect(url_for('viewGroup', groupID=groupID))

@app.route('/addBill/', methods=['GET', 'POST'])
def addBill():
    userID = current_user.get_id()
    form = BillForm()
    friends = USERS_COLLECTION.find_one({'_id': userID})['friends']
    if request.method == 'POST':
        amount = form.amount.data
        currency = form.currency.data
        topic = form.topic.data
        members = form.members.data
        pic = form.pic.data
        print(amount, currency, topic, members, pic)
        ############## not complete
    return render_template('add_bill.html', form=form, friends=friends)

@login_required
@app.route('/addFriend/', methods=['GET', 'POST'])
def addFriend():
    form = FriendForm()
    if request.method == 'POST':
        email = form.emailid.data
        usr = User(current_user.get_id())
        usr.addFriend(email)
        return redirect(url_for('dashboard'))
    return render_template('add_friend.html', form=form)


@lm.user_loader
def load_user(email):
    user = USERS_COLLECTION.find_one({'_id': email})
    if not user:
        return None
    return User(user['_id'])
