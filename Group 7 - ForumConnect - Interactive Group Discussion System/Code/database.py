import mysql.connector
from mysql.connector import Error
import logging
import time
from typing import Optional, Dict, Any

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        self.current_user_id = None
        try:
            self.connect()
        except Error as e:
            logging.error(f"Failed to initialize database: {str(e)}")
            raise

    def connect(self):
        """Connect to the database and initialize if needed"""
        try:
            if self.connection and self.connection.is_connected():
                return

            # Connection configuration without database
            config = {
                'host': 'localhost',
                'user': 'root',
                'password': 'pat@admin#0987',
                'auth_plugin': 'mysql_native_password',
                'charset': 'utf8mb4',
                'use_unicode': True,
                'get_warnings': True,
                'raise_on_warnings': True,
                'connection_timeout': 10
            }
            
            # First connect without specifying database
            self.connection = mysql.connector.connect(**config)
            self.cursor = self.connection.cursor(dictionary=True)
            
            # Check if database exists
            self.cursor.execute("SHOW DATABASES LIKE 'tk_forum'")
            database_exists = self.cursor.fetchone() is not None
            
            if database_exists:
                # Use existing database
                self.cursor.execute("USE tk_forum")
            else:
                # Create new database
                self.cursor.execute("CREATE DATABASE tk_forum")
                self.cursor.execute("USE tk_forum")
                # Create initial tables
                self.create_tables()
            
            # Set character encoding
            self.cursor.execute("SET NAMES utf8mb4")
            self.cursor.execute("SET CHARACTER SET utf8mb4")
            
            logging.info("Successfully connected to MySQL database")
            
        except Error as e:
            error_msg = str(e)
            logging.error(f"Database connection error: {error_msg}")
            if self.connection:
                try:
                    self.connection.close()
                except:
                    pass
            if self.cursor:
                try:
                    self.cursor.close()
                except:
                    pass
            self.connection = None
            self.cursor = None
            raise e

    def create_tables(self):
        """Create all necessary database tables if they don't exist"""
        try:
            # Create users table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create categories table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) UNIQUE NOT NULL
                )
            """)

            # Insert default categories if they don't exist
            self.cursor.execute("SELECT COUNT(*) as count FROM categories")
            if self.cursor.fetchone()['count'] == 0:
                self.cursor.execute("""
                    INSERT INTO categories (name) VALUES 
                    ('Music'), ('Arts'), ('Dance'), ('Entertainment'), 
                    ('Education'), ('Technology'), ('Sports'), ('Other')
                """)

            # Create posts table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    category_id INT NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    image_path VARCHAR(255) DEFAULT NULL,
                    is_locked BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
                )
            """)

            # Create replies table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS replies (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    post_id INT NOT NULL,
                    user_id INT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            # Create notifications table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    message TEXT NOT NULL,
                    is_read BOOLEAN DEFAULT FALSE,
                    notification_type VARCHAR(50) DEFAULT 'general',
                    related_post_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (related_post_id) REFERENCES posts(id) ON DELETE SET NULL
                )
            """)

            self.connection.commit()
            logging.info("Database tables verified successfully")

        except Error as e:
            logging.error(f"Error creating tables: {str(e)}")
            self.connection.rollback()
            raise

    def execute_query(self, query, params=None):
        """Execute a database query with automatic reconnection"""
        try:
            self.ensure_connection()
            
            if params is None:
                params = ()
            elif not isinstance(params, (tuple, list)):
                params = (params,)

            self.cursor.execute(query, params)
            
            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                self.connection.commit()
                if query.strip().upper().startswith('INSERT'):
                    return self.cursor.lastrowid
                return None
            
            if query.strip().upper().startswith('SELECT'):
                return self.cursor.fetchall() or []
            
            return None
            
        except Error as e:
            logging.error(f"Query execution error: {str(e)}")
            self.connection.rollback()
            raise e

    def express_travel_interest(self, current_user_id, post_owner_id, post_id):
        """Express interest in a travel post"""
        try:
            # First check if there's already an interest
            self.cursor.execute('''
                SELECT id FROM user_interests 
                WHERE user_id = %s AND interested_in_id = %s
            ''', (current_user_id, post_owner_id))
            existing_interest = self.cursor.fetchone()
            
            if existing_interest:
                # If interest exists but not accepted, update it
                self.cursor.execute('''
                    UPDATE user_interests 
                    SET accepted = FALSE 
                    WHERE id = %s
                ''', (existing_interest['id'],))
            else:
                # Create new interest
                self.cursor.execute('''
                    INSERT INTO user_interests (user_id, interested_in_id)
                    VALUES (%s, %s)
                ''', (current_user_id, post_owner_id))
            
            # Record the interest in travel posts
            self.cursor.execute('''
                INSERT INTO travel_post_interests (travel_post_id, user_id, interested_in_id)
                VALUES (%s, %s, %s)
            ''', (post_id, current_user_id, post_owner_id))
            
            self.connection.commit()
            return True
        except Error as e:
            logging.error(f"Error expressing travel interest: {str(e)}")
            return False

    def get_travel_interests(self, user_id):
        """Get all travel interests for a user"""
        try:
            self.cursor.execute('''
                SELECT tpi.travel_post_id, tp.destination, tp.travel_dates,
                       ui.accepted, u.username as interested_user,
                       u.id as interested_user_id,
                       ui.user_id as interest_initiator_id
                FROM travel_post_interests tpi
                JOIN travel_posts tp ON tp.id = tpi.travel_post_id
                JOIN user_interests ui ON ui.user_id = tpi.user_id AND ui.interested_in_id = tpi.interested_in_id
                JOIN users u ON u.id = tpi.interested_in_id
                WHERE tpi.user_id = %s OR tpi.interested_in_id = %s
                ORDER BY ui.created_at DESC
            ''', (user_id, user_id))
            return self.cursor.fetchall()
        except Error as e:
            logging.error(f"Error getting travel interests: {str(e)}")
            return []

    def accept_interest(self, interest_id, post_owner_id, interested_user_id):
        """Accept a travel interest"""
        try:
            # Update interest status
            self.cursor.execute('''
                UPDATE user_interests
                SET accepted = TRUE
                WHERE id = %s AND interested_in_id = %s
            ''', (interest_id, post_owner_id))
            
            # Create reverse interest for bidirectional chat
            self.cursor.execute('''
                INSERT INTO user_interests (user_id, interested_in_id, accepted)
                SELECT %s, %s, TRUE
                WHERE NOT EXISTS (
                    SELECT 1 FROM user_interests 
                    WHERE user_id = %s AND interested_in_id = %s
                )
            ''', (interested_user_id, post_owner_id, interested_user_id, post_owner_id))
            
            self.connection.commit()
            return True
        except Error as e:
            logging.error(f"Error accepting interest: {str(e)}")
            return False

    def can_chat(self, user_id, other_user_id):
        """Check if two users can chat"""
        try:
            self.cursor.execute('''
                SELECT COUNT(*) as count
                FROM user_interests
                WHERE ((user_id = %s AND interested_in_id = %s) OR
                       (user_id = %s AND interested_in_id = %s))
                AND accepted = TRUE
            ''', (user_id, other_user_id, other_user_id, user_id))
            result = self.cursor.fetchone()
            return result['count'] > 0
        except Error as e:
            logging.error(f"Error checking chat permission: {str(e)}")
            return False

    def add_travel_interest(self, travel_post_id, interested_user_id):
        """
        Add a new interest to a travel post and notify the post creator
        """
        try:
            # Add interest
            self.cursor.execute('''
                INSERT INTO travel_post_interests (travel_post_id, user_id, interested_in_id)
                VALUES (%s, %s, %s)
            ''', (travel_post_id, interested_user_id, interested_user_id))

            # Get post creator
            self.cursor.execute('''
                SELECT user_id FROM travel_posts WHERE id = %s
            ''', (travel_post_id,))
            post_creator_id = self.cursor.fetchone()['user_id']

            # Get destination
            self.cursor.execute('''
                SELECT destination FROM travel_posts WHERE id = %s
            ''', (travel_post_id,))
            destination = self.cursor.fetchone()['destination']

            # Notify post creator
            self.cursor.execute('''
                INSERT INTO notifications (user_id, message, notification_type, related_post_id)
                VALUES (%s, %s, %s, %s)
            ''', (
                post_creator_id,
                f"Someone is interested in your travel post to {destination}",
                'travel_interest',
                travel_post_id
            ))

            self.connection.commit()
            return True
        except Error as e:
            logging.error(f"Error adding travel interest: {str(e)}")
            self.connection.rollback()
            return False

    def get_notifications(self, user_id):
        """
        Get all notifications for a user
        """
        try:
            self.cursor.execute('''
                SELECT n.*, tp.destination 
                FROM notifications n
                LEFT JOIN travel_posts tp ON n.related_post_id = tp.id
                WHERE n.user_id = %s
                ORDER BY n.created_at DESC
            ''', (user_id,))
            return self.cursor.fetchall()
        except Error as e:
            logging.error(f"Error getting notifications: {str(e)}")
            return []

    def mark_notification_read(self, notification_id):
        """
        Mark a notification as read
        """
        try:
            self.cursor.execute('''
                UPDATE notifications SET is_read = TRUE WHERE id = %s
            ''', (notification_id,))
            self.connection.commit()
            return True
        except Error as e:
            logging.error(f"Error marking notification as read: {str(e)}")
            self.connection.rollback()
            return False

    def add_travel_plan(self, user_id, destination, start_date, end_date, description, max_travelers):
        """Add a new travel plan"""
        try:
            self.cursor.execute('''
                INSERT INTO travel_plans (user_id, destination, start_date, end_date, description, max_travelers)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (user_id, destination, start_date, end_date, description, max_travelers))
            self.connection.commit()
            return self.cursor.lastrowid
        except Error as e:
            logging.error(f"Error adding travel plan: {str(e)}")
            self.connection.rollback()
            return None

    def get_travel_plans(self):
        try:
            query = """
            SELECT 
                tp.*,
                u.username,
                (SELECT COUNT(*) FROM travel_buddies WHERE plan_id = tp.id AND status = 'accepted') as current_buddies,
                (SELECT COUNT(*) FROM travel_buddies WHERE plan_id = tp.id) as interest_count,
                DATE_FORMAT(tp.start_date, '%Y-%m-%d') as formatted_start_date,
                DATE_FORMAT(tp.end_date, '%Y-%m-%d') as formatted_end_date
            FROM travel_plans tp
            JOIN users u ON tp.user_id = u.id
            WHERE tp.start_date >= CURDATE()
            ORDER BY tp.start_date ASC
            """
            return self.execute_query(query)
        except Exception as e:
            logging.error(f"Error loading travel plans: {str(e)}")
            return []

    def get_my_travel_plans(self, user_id):
        """Get travel plans created by or joined by the user"""
        try:
            # Query to get both created and joined plans
            query = """
            SELECT 
                tp.*,
                u.username,
                (SELECT COUNT(*) FROM travel_buddies WHERE plan_id = tp.id AND status = 'accepted') as current_buddies,
                (SELECT COUNT(*) FROM travel_buddies WHERE plan_id = tp.id) as interest_count,
                DATE_FORMAT(tp.start_date, '%Y-%m-%d') as formatted_start_date,
                DATE_FORMAT(tp.end_date, '%Y-%m-%d') as formatted_end_date,
                CASE 
                    WHEN tp.user_id = %s THEN 'created'
                    WHEN tb.status = 'accepted' THEN 'joined'
                    WHEN tb.status = 'pending' THEN 'pending'
                    WHEN tb.status = 'rejected' THEN 'rejected'
                    ELSE NULL
                END as relationship_type
            FROM travel_plans tp
            JOIN users u ON tp.user_id = u.id
            LEFT JOIN travel_buddies tb ON tp.id = tb.plan_id AND tb.user_id = %s
            WHERE tp.user_id = %s  -- Plans created by user
               OR (tb.user_id = %s AND tb.status = 'accepted')  -- Plans joined by user
               OR (tb.user_id = %s AND tb.status = 'pending')   -- Plans with pending interest
            ORDER BY tp.start_date ASC
            """
            return self.execute_query(query, (user_id, user_id, user_id, user_id, user_id))
        except Exception as e:
            logging.error(f"Error getting user's travel plans: {str(e)}")
            return []

    def delete_travel_plan(self, plan_id, user_id):
        """Delete a travel plan"""
        try:
            # Verify ownership
            self.cursor.execute('''
                SELECT user_id FROM travel_posts WHERE id = %s
            ''', (plan_id,))
            plan = self.cursor.fetchone()
            
            if not plan or plan['user_id'] != user_id:
                return False

            # Delete the plan (cascade will handle related records)
            self.cursor.execute('''
                DELETE FROM travel_posts WHERE id = %s AND user_id = %s
            ''', (plan_id, user_id))
            self.connection.commit()
            return True
        except Error as e:
            logging.error(f"Error deleting travel plan: {str(e)}")
            self.connection.rollback()
            return False

    def __del__(self):
        """Clean up database resources"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
                logging.info("Database connection closed.")
        except Exception as e:
            logging.error(f"Error closing database connection: {str(e)}")

    def ensure_connection(self):
        """Ensure database connection is active"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            self.connection.ping(reconnect=True, attempts=3, delay=5)
        except Error as e:
            logging.error(f"Connection error: {str(e)}")
            self.connect()

    def reconnect(self):
        """Reconnect to the database"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            self.connection = None
            self.cursor = None
            self.connect()
        except Error as e:
            logging.error(f"Reconnection error: {str(e)}")
            raise e

    def handle_travel_interest(self, plan_id, user_id, action):
        """Handle accepting or rejecting travel interest"""
        try:
            # Update the interest status
            self.cursor.execute("""
                UPDATE travel_buddies 
                SET status = %s 
                WHERE plan_id = %s AND user_id = %s
            """, (action, plan_id, user_id))

            # Get plan and user details for notification
            plan_details = self.execute_query("""
                SELECT tp.destination, tp.user_id as owner_id, u.username,
                       (SELECT username FROM users WHERE id = %s) as interested_username
                FROM travel_plans tp
                JOIN users u ON tp.user_id = u.id
                WHERE tp.id = %s
            """, (user_id, plan_id))

            if plan_details:
                plan = plan_details[0]
                # Create notification for the interested user
                notification_message = f"Your interest in the travel plan to {plan['destination']} has been {action}"
                self.execute_query("""
                    INSERT INTO notifications 
                    (user_id, message, notification_type, related_post_id, is_read)
                    VALUES (%s, %s, 'interest_response', %s, 0)
                """, (user_id, notification_message, plan_id))

                # If accepted, create a notification for the plan owner
                if action == 'accepted':
                    owner_message = f"{plan['interested_username']} has joined your travel plan to {plan['destination']}"
                    self.execute_query("""
                        INSERT INTO notifications 
                        (user_id, message, notification_type, related_post_id, is_read)
                        VALUES (%s, %s, 'travel_joined', %s, 0)
                    """, (plan['owner_id'], owner_message, plan_id))

            self.connection.commit()
            return True
        except Exception as e:
            logging.error(f"Error handling travel interest: {str(e)}")
            self.connection.rollback()
            return False

    def express_interest_in_plan(self, plan_id, user_id, message=""):
        """Express interest in a travel plan"""
        try:
            # Check if already expressed interest
            existing = self.execute_query("""
                SELECT id, status FROM travel_buddies 
                WHERE plan_id = %s AND user_id = %s
            """, (plan_id, user_id))

            if existing:
                return False, "You have already expressed interest in this plan"

            # Check if user is the plan creator
            plan = self.execute_query("""
                SELECT tp.*, u.username, 
                       (SELECT username FROM users WHERE id = %s) as interested_username
                FROM travel_plans tp 
                JOIN users u ON tp.user_id = u.id 
                WHERE tp.id = %s
            """, (user_id, plan_id))

            if not plan:
                return False, "Travel plan not found"

            plan = plan[0]
            
            if plan['user_id'] == user_id:
                return False, "You cannot express interest in your own plan"

            # Add interest record
            self.execute_query("""
                INSERT INTO travel_buddies (plan_id, user_id, status, message)
                VALUES (%s, %s, 'pending', %s)
            """, (plan_id, user_id, message))

            # Create notification for plan owner
            notification_message = f"{plan['interested_username']} has expressed interest in your travel plan to {plan['destination']}"
            self.execute_query("""
                INSERT INTO notifications 
                (user_id, message, notification_type, related_post_id, related_user_id, is_read)
                VALUES (%s, %s, 'travel_interest', %s, %s, 0)
            """, (plan['user_id'], notification_message, plan_id, user_id))

            self.connection.commit()
            return True, "Interest expressed successfully"
        except Exception as e:
            logging.error(f"Error expressing interest in plan: {str(e)}")
            self.connection.rollback()
            return False, str(e)

    def delete_post(self, post_id, user_id):
        """Delete a post and all its replies"""
        try:
            # Verify ownership
            self.cursor.execute("""
                SELECT user_id FROM posts WHERE id = %s
            """, (post_id,))
            post = self.cursor.fetchone()
            
            if not post or post['user_id'] != user_id:
                return False, "You can only delete your own posts"

            # Delete the post (cascade will handle replies)
            self.cursor.execute("""
                DELETE FROM posts WHERE id = %s AND user_id = %s
            """, (post_id, user_id))
            
            self.connection.commit()
            return True, "Post deleted successfully"
        except Error as e:
            logging.error(f"Error deleting post: {str(e)}")
            self.connection.rollback()
            return False, str(e)

    def delete_reply(self, reply_id, user_id):
        """Delete a reply from the database"""
        try:
            # First check if the user has permission to delete this reply
            self.cursor.execute("""
                SELECT r.user_id, r.post_id, p.user_id as post_owner_id
                FROM replies r
                JOIN posts p ON r.post_id = p.id
                WHERE r.id = %s
            """, (reply_id,))
            reply = self.cursor.fetchone()
            
            if not reply:
                return False, "Reply not found"
            
            # Allow deletion if user is reply owner or post owner
            if user_id != reply['user_id'] and user_id != reply['post_owner_id']:
                return False, "You don't have permission to delete this reply"
            
            # Delete the reply
            self.cursor.execute("""
                DELETE FROM replies WHERE id = %s
            """, (reply_id,))
            
            # Check if this was the last reply and update post lock status if needed
            self.cursor.execute("""
                UPDATE posts 
                SET is_locked = CASE 
                    WHEN (SELECT COUNT(*) FROM replies WHERE post_id = %s) = 0 THEN 0
                    ELSE is_locked 
                END
                WHERE id = %s
            """, (reply['post_id'], reply['post_id']))
            
            self.connection.commit()
            return True, "Reply deleted successfully"
            
        except Error as e:
            logging.error(f"Error deleting reply: {str(e)}")
            self.connection.rollback()
            return False, "Failed to delete reply"

    def delete_chat(self, chat_id, user_id):
        """Delete a chat message"""
        try:
            # Verify ownership
            self.cursor.execute("""
                SELECT * FROM chat_messages WHERE id = %s
            """, (chat_id,))
            chat = self.cursor.fetchone()
            
            if not chat:
                return False, "Chat message not found"
                
            if chat['sender_id'] != user_id:
                return False, "You can only delete your own messages"

            # Delete the chat message
            self.cursor.execute("""
                DELETE FROM chat_messages WHERE id = %s AND sender_id = %s
            """, (chat_id, user_id))
            
            self.connection.commit()
            return True, "Message deleted successfully"
        except Error as e:
            logging.error(f"Error deleting chat message: {str(e)}")
            self.connection.rollback()
            return False, str(e)

    def can_reply_to_post(self, post_id):
        """Check if a user can reply to a post"""
        try:
            # Get post and reply information
            self.cursor.execute("""
                SELECT 
                    p.user_id as post_owner_id,
                    p.is_locked,
                    (SELECT COUNT(*) FROM replies WHERE post_id = p.id) as reply_count,
                    (SELECT user_id FROM replies 
                     WHERE post_id = p.id 
                     ORDER BY created_at ASC LIMIT 1) as first_replier_id
                FROM posts p
                WHERE p.id = %s
            """, (post_id,))
            
            result = self.cursor.fetchone()
            if not result:
                return False, "Post not found"
            
            # Post owner can always reply
            if result['post_owner_id'] == self.current_user_id:
                return True, "Can reply to post"
            
            # If there are no replies yet, anyone can reply
            if result['reply_count'] == 0:
                return True, "Can reply to post"
            
            # If there are replies and post is locked, only first replier can continue
            if result['is_locked']:
                if result['first_replier_id'] == self.current_user_id:
                    return True, "Can reply to post"
                return False, "Only the post owner and first replier can reply to this post"
            
            return True, "Can reply to post"
            
        except Error as e:
            logging.error(f"Error checking reply permission: {str(e)}")
            return False, str(e)

    def add_reply(self, post_id, user_id, content):
        """Add a reply to a post"""
        try:
            # First check if user can reply
            can_reply, message = self.can_reply_to_post(post_id)
            if not can_reply:
                return False, message
            
            # Insert the reply
            self.cursor.execute("""
                INSERT INTO replies (post_id, user_id, content)
                VALUES (%s, %s, %s)
            """, (post_id, user_id, content))
            
            reply_id = self.cursor.lastrowid
            
            # Lock the post if this is the first reply and user is not post owner
            self.cursor.execute("""
                UPDATE posts p
                SET is_locked = TRUE
                WHERE p.id = %s
                AND (SELECT COUNT(*) FROM replies WHERE post_id = p.id) = 1
                AND p.user_id != %s
            """, (post_id, user_id))
            
            # Get post owner for notification
            self.cursor.execute("""
                SELECT user_id FROM posts WHERE id = %s
            """, (post_id,))
            post = self.cursor.fetchone()
            
            # Create notification for post owner if reply is from someone else
            if post and post['user_id'] != user_id:
                self.cursor.execute("""
                    INSERT INTO notifications (user_id, message, notification_type, related_post_id)
                    VALUES (%s, %s, 'new_reply', %s)
                """, (post['user_id'], "Someone replied to your post", post_id))
            
            self.connection.commit()
            return True, reply_id
            
        except Error as e:
            logging.error(f"Error adding reply: {str(e)}")
            self.connection.rollback()
            return False, str(e)

    def get_replies(self, post_id):
        """Get all replies for a post with user information"""
        try:
            self.cursor.execute("""
                SELECT 
                    r.id as reply_id,
                    r.content,
                    r.created_at,
                    r.user_id,
                    u.username,
                    p.user_id as post_owner_id,
                    p.is_locked
                FROM replies r
                JOIN users u ON r.user_id = u.id
                JOIN posts p ON r.post_id = p.id
                WHERE r.post_id = %s
                ORDER BY r.created_at ASC
            """, (post_id,))
            
            replies = self.cursor.fetchall()
            return True, replies
            
        except Error as e:
            logging.error(f"Error getting replies: {str(e)}")
            return False, []

    def update_reply(self, reply_id, user_id, new_content):
        """Update a reply's content"""
        try:
            # Check if user owns the reply
            self.cursor.execute("""
                SELECT user_id FROM replies 
                WHERE id = %s
            """, (reply_id,))
            reply = self.cursor.fetchone()
            
            if not reply:
                return False, "Reply not found"
                
            if reply['user_id'] != user_id:
                return False, "You can only edit your own replies"
            
            # Update the reply
            self.cursor.execute("""
                UPDATE replies 
                SET content = %s 
                WHERE id = %s AND user_id = %s
            """, (new_content, reply_id, user_id))
            
            self.connection.commit()
            return True, "Reply updated successfully"
            
        except Error as e:
            logging.error(f"Error updating reply: {str(e)}")
            self.connection.rollback()
            return False, str(e)

    def set_current_user(self, user_id):
        """Set the current user ID"""
        self.current_user_id = user_id