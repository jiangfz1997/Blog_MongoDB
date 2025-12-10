<template>
  <section class="max-w-4xl mx-auto mt-10 p-4">
    <h2 class="text-xl font-semibold mb-6">Comments ({{ commentsData.total }})</h2>

    <div class="flex gap-4 mb-8">
      <img v-if="userStore.user?.avatar_url"
                    :src="userStore.user.avatar_url" class="w-12 h-12 rounded-full bg-gray-100" alt="My Avatar"/>

      <div class="flex-1">
        <textarea
          v-model="newCommentContent"
          :placeholder="userStore.user?.id ? 'Add to the discussion...' : 'Please login to comment'"
          :disabled="!userStore.user?.id"
          rows="3"
          class="w-full bg-gray-100 border border-transparent rounded-lg p-3 focus:bg-white focus:border-blue-400 focus:ring-2 focus:ring-blue-100 outline-none transition-all resize-none text-sm"
        ></textarea>
        <div class="flex justify-end mt-2">
          <button @click="postRootComment" :disabled="!userStore.user?.id ||!newCommentContent.trim()" class="bg-blue-500 hover:bg-blue-600 text-white text-sm px-6 py-2 rounded-full disabled:opacity-50 transition-colors font-medium">
            Comment
          </button>
        </div>
      </div>
    </div>

    <div class="space-y-8">
      <div v-for="rootComment in commentsData.items" :key="rootComment.id">
        
        <div class="flex gap-4 group">
          <div class="flex-shrink-0 cursor-pointer">
            <img :src="rootComment.author_avatar" alt="avatar" class="w-10 h-10 rounded-full border border-gray-100"/>
          </div>

          <div class="flex-1">
            <div class="text-sm font-bold text-gray-600 mb-1 cursor-pointer hover:text-blue-500">
              {{ rootComment.author_username }}
            </div>
            <p class="text-gray-800 text-base leading-relaxed mb-2">{{ rootComment.content }}</p>

            <div class="flex items-center gap-4 text-xs text-gray-400 mb-3">
              <span>{{ formatDate(rootComment.created_at) }}</span>
              <button 
                @click="openReplyBox(rootComment, rootComment.id)" 
                class="hover:text-blue-500 cursor-pointer transition-colors"
                v-if="userStore.user?.id"
              >
                Reply
              </button>
              <!-- <button class="hover:text-red-500 cursor-pointer transition-colors">Like</button> -->
              <button 
                v-if="userStore.user?.id === rootComment.author_id"
                @click="handleDelete(rootComment, true)"
                class="hover:text-red-500 cursor-pointer transition-colors"
              >Delete</button>

            </div>

            <div v-if="replyBoxState.parentId === rootComment.id" class="mb-4 animate-fade-in-down">
              <div class="flex gap-3">
                 <textarea
                  v-model="replyBoxState.content"
                  :placeholder="`Reply to @${replyBoxState.username}...`"
                  rows="2"
                  class="w-full bg-white border border-blue-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-100 outline-none resize-none text-sm"
                  autofocus
                ></textarea>
              </div>
              <div class="flex justify-end gap-2 mt-2">
                <button @click="closeReplyBox" class="text-gray-500 text-xs hover:text-gray-700 px-3 py-1">Cancel</button>
                <button @click="postSubComment" class="bg-blue-500 text-white text-xs px-4 py-1.5 rounded-full hover:bg-blue-600">Reply</button>
              </div>
            </div>

            <div 
              v-if="rootComment.replies && rootComment.replies.length > 0" 
              class="bg-gray-50/80 p-3 rounded-lg space-y-3"
            >
              <div v-for="reply in rootComment.replies" :key="reply.id" class="text-sm group/reply">
                <div class="flex items-start gap-2">
                  <img :src="reply.author_avatar" class="w-6 h-6 rounded-full mt-0.5"/>
                  
                  <div class="flex-1">
                    <span class="text-gray-800">
                      <span class="font-medium text-blue-500 cursor-pointer hover:text-blue-600">{{ reply.author_username }}</span>
                      <template v-if="reply.reply_to_username && reply.reply_to_comment_id !== rootComment.id">
                        <span class="mx-1 text-gray-500">Reply</span>
                        <span class="font-medium text-blue-500 cursor-pointer hover:text-blue-600">@{{ reply.reply_to_username }}</span>
                      </template>
                      <span class="mx-1 text-gray-800">:</span>
                      {{ reply.content }}
                    </span>

                    <div class="flex items-center gap-3 mt-1 text-xs text-gray-400">
                      <span>{{ formatDate(reply.created_at) }}</span>
                      <button 
                        @click="openReplyBox(reply, rootComment.id)"
                                                v-if="userStore.user?.id"
                        class="hover:text-blue-500 cursor-pointer hidden group-hover/reply:block"
                      >
                        Reply
                      </button>
                      <!-- <button class="hover:text-red-500 cursor-pointer hidden group-hover/reply:block">Like</button> -->
                      <button 
                          v-if="userStore.user?.id === reply.author_id"
                          @click="handleDelete(reply, true)"
                          class="hover:text-red-500 cursor-pointer hidden group-hover/reply:block"
                        > Delete
                      </button>
                      
                    </div>

                    <div v-if="replyBoxState.parentId === reply.id" class="mt-2 ml-2">
                       <div class="flex flex-col gap-2">
                        <textarea
                          v-model="replyBoxState.content"
                          :placeholder="`Reply to @${replyBoxState.username}...`"
                          rows="2"
                          class="w-full bg-white border border-blue-300 rounded p-2 text-xs focus:ring-1 focus:ring-blue-200 outline-none resize-none"
                          autofocus
                        ></textarea>
                        <div class="flex justify-end gap-2">
                          <button @click="closeReplyBox" class="text-gray-500 text-xs hover:text-gray-700">Cancel</button>
                          <button @click="postSubComment" class="bg-blue-500 text-white text-xs px-3 py-1 rounded hover:bg-blue-600">Reply</button>
                        </div>
                      </div>
                    </div>

                  </div>
                </div>
              </div>
              
              <div v-if="rootComment.replies_has_next" @click="loadMoreReplies(rootComment)" class="text-xs text-blue-500 cursor-pointer pt-1 hover:underline">
                View more replies ({{ rootComment.replies_total }} total)
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>

    <div v-if="commentsData.items.length === 0" class="text-center text-gray-400 py-10">
      No comments yet, be the first to comment!
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { postComment, getComments, formatDate, getMoreReplies, deleteComment } from '@/api/comments.js'
import { useUserStore } from '@/store/userStore'
const props = defineProps({
  blogId: {
    type: String,
    required: true
  }
})
const commentsData = ref({items: [], total: 0})
const loading = ref(false)
const newCommentContent = ref('')
const userStore = useUserStore()
const replyBoxState = ref({
  parentId: null, 
  rootId: null,   
  username: '',   
  content: '' 
})
const fetchComments = async () => {
  if (!props.blogId) return
  
  loading.value = true
  try {

    const data = await getComments(props.blogId, 1, 20)
    console.log('Fetched comments:', data)
    commentsData.value = data
  } catch (error) {
    console.error('Failed to load comments:', error)
  } finally {
    loading.value = false
  }
}

const openReplyBox = (comment, rootId) => {
  if (replyBoxState.value.parentId === comment.id) {
    closeReplyBox()
    return
  }
  
  replyBoxState.value = {
    parentId: comment.id,
    rootId: rootId, 
    username: comment.author_username,
    content: ''
  }
}

const closeReplyBox = () => {
  replyBoxState.value = { parentId: null, rootId: null, username: '', content: '' }
}

const postSubComment = async () => {
  if (!replyBoxState.value.content.trim()) return

  const { parentId, rootId, content } = replyBoxState.value
  try {
    const newReply = await postComment(props.blogId, content, parentId)
    
    const rootComment = commentsData.value.items.find(item => item.id === rootId)
    if (rootComment) {
      if (!rootComment.replies) rootComment.replies = []
      
      rootComment.replies.push(newReply)
      rootComment.replies_total = (rootComment.replies_total || 0) + 1
    }

    closeReplyBox()
    await fetchComments()
  } catch (error) {
    console.error('Error posting reply:', error)
  }
}

const loadMoreReplies = async (rootComment) => {
  if (rootComment.isLoadingMore) return

  rootComment.isLoadingMore = true
  
  try {
    const currentPage = rootComment.replies_page || 1
    const nextPage = currentPage + 1
    const size = rootComment.replies_size || 5 
    const data = await getMoreReplies(rootComment.id, nextPage, size)
    
    if (data && data.items) {
      rootComment.replies.push(...data.items)
      
      rootComment.replies_page = nextPage

      rootComment.replies_has_next = data.has_next
    }
  } catch (error) {
    console.error('Failed to load more replies:', error)
  } finally {
    rootComment.isLoadingMore = false
  }
}

const handleDelete = async (comment, isRoot, parentComment = null) => {
  if (!confirm('Are you sure you want to delete this comment?')) return

  try {
    const res = await deleteComment(comment.id, props.blogId)
    
    if (isRoot) {
        commentsData.value.items = commentsData.value.items.filter(c => c.id !== comment.id)
        commentsData.value.total--
    } else if (parentComment) {
        parentComment.replies = parentComment.replies.filter(r => r.id !== comment.id)
        parentComment.replies_total--
    }
    
    await fetchComments()
  } catch (error) {
    console.error('Delete failed', error)
  }
}


onMounted(() => {
  fetchComments()
})

watch(() => props.blogId, (newId) => {
  if (newId) fetchComments()
})

// const commentsData = ref({
//   "items": [
//     {
//       "id": "691e2bb6c8e6905d50871ba6",
//       "blog_id": "691bd8a120d5dc3ada9052df",
//       "author_id": "691bcc477b6afcd1e2a1a0a5",
//       "author_username": "AdventureKing", 
//       "content": "First root comment: Is this really simpler than Vue 2?",
//       "created_at": "2025-11-19T20:42:30.993000",
//       "is_root": true,
//       "root_id": "691e2bb6c8e6905d50871ba6",
//       "parent_id": null,
//       "replies": [
//         {
//           "id": "691e2bd2c8e6905d50871ba7",
//           "blog_id": "691bd8a120d5dc3ada9052df",
//           "author_id": "691bcc477b6afcd1e2a1a0a5",
//           "author_username": "VueFan123",
//           "content": "This is the first sub comment directly to root.",
//           "created_at": "2025-11-19T20:42:58.917000",
//           "is_root": false,
//           "root_id": "691e2bb6c8e6905d50871ba6",
//           "parent_id": "691e2bb6c8e6905d50871ba6",
//           "reply_to_comment_id": "691e2bb6c8e6905d50871ba6",
//           "reply_to_username": "AdventureKing"
//         },
//         {
//           "id": "691e2bf5c8e6905d50871ba8",
//           "blog_id": "691bd8a120d5dc3ada9052df",
//           "author_id": "691bcc477b6afcd1e2a1a0a5",
//           "author_username": "ReactLover",
//           "content": "Reply to the sub comment above me.",
//           "created_at": "2025-11-19T20:43:33.989000",
//           "is_root": false,
//           "root_id": "691e2bb6c8e6905d50871ba6",
//           "parent_id": "691e2bd2c8e6905d50871ba7",
//           "reply_to_comment_id": "691e2bd2c8e6905d50871ba7", 
//           "reply_to_username": "VueFan123"
//         }
//       ],
//       "replies_total": 2,
//       "replies_has_next": false
//     },
//     {
//       "id": "691e2c08c8e6905d50871ba9",
//       "blog_id": "691bd8a120d5dc3ada9052df",
//       "author_id": "691bcc477b6afcd1e2a1a0a5",
//       "author_username": "TechGuru",
//       "content": "Second root comment here. No replies yet.",
//       "created_at": "2025-11-19T20:43:52.485000",
//       "is_root": true,
//       "root_id": "691e2c08c8e6905d50871ba9",
//       "parent_id": null,
//       "replies": [],
//       "replies_total": 0,
//       "replies_has_next": false
//     }
//   ],
//   "total": 2
// })



// Post root comment logic (frontend demonstration only)
const postRootComment = async () => {
  if (!newCommentContent.value.trim()) return
  try {
    const newComment = await postComment(props.blogId,newCommentContent.value, null)
    if (commentsData.value.items) {
      commentsData.value.items.unshift(newComment)
      
      // Update total count if necessary
      commentsData.value.total = (commentsData.value.total || 0) + 1
    }
    newCommentContent.value = ''
  } catch (error) {
    console.error('Error posting root comment:', error)
  }  
}
</script>