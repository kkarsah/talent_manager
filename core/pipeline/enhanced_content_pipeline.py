# ============================================================================
# ENHANCED CONTENT PIPELINE INTEGRATION
# core/pipeline/enhanced_content_pipeline.py (UPDATED)
# ============================================================================


class EnhancedContentPipeline:
    """Enhanced pipeline with autonomous research integration"""

    async def create_enhanced_content(
        self,
        talent_name: str,
        topic: str = None,
        content_type: str = "long_form",
        auto_upload: bool = False,
        use_runway: bool = False,
        research_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Enhanced content creation with autonomous research context"""

        job_id = f"enhanced_{talent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        try:
            logger.info(
                f"🎬 Starting autonomous enhanced content creation for {talent_name}"
            )

            # If no topic provided, use autonomous research to find one
            if not topic:
                topic = await self._autonomous_topic_selection(talent_name)

            # Generate enhanced content with research context
            enhanced_script_data = await self._generate_contextual_content(
                talent_name, topic, content_type, research_context
            )

            # Extract scripts
            full_enhanced_script = enhanced_script_data.get("enhanced_script", "")

            # Clean script for TTS
            from core.content.script_cleaner import ScriptCleaner

            tts_script = ScriptCleaner.extract_spoken_content(
                full_enhanced_script, talent_name
            )

            logger.info(
                f"📊 Script processing: {len(full_enhanced_script)} → {len(tts_script)} chars"
            )

            # Generate audio
            voice_settings = await self._get_voice_settings(talent_name)
            audio_path = await self.tts_service.generate_speech(
                tts_script, voice_settings, f"autonomous_audio_{job_id}.mp3"
            )

            # Create enhanced video
            video_path = await self._create_enhanced_video(
                full_enhanced_script,
                audio_path,
                enhanced_script_data.get("title", topic),
                content_type,
                talent_name,
            )

            # Generate optimized metadata
            optimized_metadata = await self._generate_optimized_metadata(
                enhanced_script_data, research_context
            )

            # Upload if requested
            youtube_url = None
            if auto_upload and video_path:
                youtube_url = await self._upload_with_optimized_metadata(
                    video_path, optimized_metadata
                )

            # Save to database with autonomous flags
            await self._save_autonomous_content(
                job_id=job_id,
                talent_name=talent_name,
                enhanced_script_data=enhanced_script_data,
                tts_script=tts_script,
                audio_path=audio_path,
                video_path=video_path,
                youtube_url=youtube_url,
                research_context=research_context,
                autonomous=True,
            )

            return {
                "success": True,
                "job_id": job_id,
                "talent_name": talent_name,
                "title": enhanced_script_data.get("title", topic),
                "topic": topic,
                "content_type": content_type,
                "autonomous": True,
                "research_driven": research_context is not None,
                "audio_path": audio_path,
                "video_path": video_path,
                "youtube_url": youtube_url,
                "metadata": optimized_metadata,
                "tts_script_length": len(tts_script),
                "full_script_length": len(full_enhanced_script),
            }

        except Exception as e:
            logger.error(f"❌ Autonomous enhanced content creation failed: {e}")
            return {
                "success": False,
                "job_id": job_id,
                "talent_name": talent_name,
                "topic": topic,
                "error": str(e),
                "autonomous": True,
            }

    async def _autonomous_topic_selection(self, talent_name: str) -> str:
        """Autonomous topic selection using research"""

        # Get talent specialization
        talent_specialization = self._get_talent_specialization(talent_name)

        # Perform quick research
        async with AutonomousResearcher(talent_specialization) as researcher:
            topics = await researcher.research_trending_topics(limit=20)

        if topics:
            # Select best topic
            best_topic = topics[0]
            return best_topic.title
        else:
            # Fallback to curated topics
            fallback_topics = {
                "tech_education": "Latest Programming Trends Every Developer Should Know",
                "cooking": "Quick and Healthy Weeknight Dinner Ideas",
                "fitness": "Complete Bodyweight Workout for Beginners",
            }
            return fallback_topics.get(
                talent_specialization, "Trending Topics in Your Field"
            )

    async def _generate_contextual_content(
        self,
        talent_name: str,
        topic: str,
        content_type: str,
        research_context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Generate content with research context integration"""

        # Enhanced prompt with research context
        context_prompt = ""
        if research_context:
            context_prompt = f"""
            Research Context:
            - Source: {research_context.get('source', 'Unknown')}
            - Category: {research_context.get('category', 'General')}
            - Key Points: {research_context.get('key_points', [])}
            - Target Audience: {research_context.get('target_audience', 'General')}
            - Content Potential Score: {research_context.get('content_potential', 0)}
            
            Use this research context to create highly relevant, trending content that addresses current interests in the field.
            """

        # Generate enhanced script with context
        if talent_name.lower() in ["alex", "alex_codemaster"]:
            content = await self._generate_alex_contextual_content(
                topic, content_type, context_prompt
            )
        else:
            content = await self._generate_generic_contextual_content(
                talent_name, topic, content_type, context_prompt
            )

        return content

    async def _generate_optimized_metadata(
        self, script_data: Dict[str, Any], research_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate SEO-optimized metadata using research insights"""

        base_metadata = {
            "title": script_data.get("title", ""),
            "description": script_data.get("description", ""),
            "tags": script_data.get("tags", []),
        }

        if research_context:
            # Enhance with research-driven keywords
            research_keywords = research_context.get("keywords", [])
            base_metadata["tags"].extend(
                research_keywords[:10]
            )  # Add top 10 research keywords

            # Optimize title with trending terms
            if research_context.get("trending_score", 0) > 0.7:
                base_metadata["title"] = f"🔥 {base_metadata['title']}"

            # Add source attribution if relevant
            if research_context.get("source_url"):
                base_metadata["source_inspiration"] = research_context["source_url"]

        return base_metadata
