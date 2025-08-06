from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from news.models import Category, Article
from django.utils import timezone

class Command(BaseCommand):
    help = 'Create sample categories and articles for testing'

    def handle(self, *args, **options):
        # Get or create a user
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created user: {user.username}'))

        # Remove duplicate Education categories if any
        education_cats = Category.objects.filter(name='Education')
        if education_cats.count() > 1:
            # Keep the first, delete the rest
            for cat in education_cats[1:]:
                cat.delete()
                self.stdout.write(self.style.SUCCESS('Removed duplicate Education category'))

        # Create sample categories (ensure only one Education, add Achievements)
        categories_data = [
            {
                'name': 'Technology',
                'description': 'Latest technology news and updates'
            },
            {
                'name': 'Sports',
                'description': 'Sports news and updates'
            },
            {
                'name': 'Education',
                'description': 'Educational news and updates'
            },
            {
                'name': 'Health',
                'description': 'Health and wellness news and updates'
            },
            {
                'name': 'Achievements',
                'description': 'School achievements, awards, and recognitions'
            }
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories.append(category)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))

        # Create sample articles - 4 articles per category
        articles_data = [
            # Technology Articles (4)
            {
                'title': 'New AI Technology Breakthrough',
                'content': '''Artificial Intelligence has taken a giant leap forward with the latest breakthrough in machine learning algorithms. Researchers have developed a new neural network architecture that can process information 10 times faster than previous models.

The new technology, called "Quantum Neural Processing," combines quantum computing principles with traditional neural networks to create a hybrid system that's both powerful and efficient.

"This is a game-changer for the AI industry," says Dr. Sarah Johnson, lead researcher at the AI Institute. "We're seeing performance improvements that we didn't think were possible with current technology."

The breakthrough has implications for various industries including healthcare, finance, and autonomous vehicles. Early tests show that the new system can diagnose medical conditions with 99.7% accuracy and process financial transactions in real-time.

Companies are already lining up to license this technology, with major tech giants expressing interest in implementing it in their products.''',
                'excerpt': 'A revolutionary new AI technology that combines quantum computing with neural networks has been developed, promising unprecedented performance improvements.',
                'category': 'Technology',
                'status': 'published'
            },
            {
                'title': 'Latest Smartphone Features Revealed',
                'content': '''The newest smartphone from TechCorp has been unveiled, featuring cutting-edge technology that sets a new standard for mobile devices. The TechCorp Pro X includes a revolutionary foldable display, advanced AI capabilities, and a battery that lasts up to 48 hours on a single charge.

The foldable display technology allows users to transform their phone into a tablet-sized device, providing a larger screen for productivity and entertainment. The AI assistant can now understand context and provide more personalized responses.

"We've pushed the boundaries of what's possible with mobile technology," says TechCorp CEO Lisa Rodriguez. "The Pro X represents the future of smartphones."

The device also includes a 200-megapixel camera system with advanced night mode and AI-powered photo editing. The security features include facial recognition, fingerprint scanning, and voice authentication.

Pre-orders for the TechCorp Pro X begin next week, with the first shipments expected in December. The phone will be available in three colors: Cosmic Black, Lunar Silver, and Aurora Blue.''',
                'excerpt': 'TechCorp Pro X smartphone unveiled with foldable display, AI capabilities, and 48-hour battery life, setting new standards for mobile technology.',
                'category': 'Technology',
                'status': 'published'
            },
            {
                'title': 'Blockchain Revolution in Finance',
                'content': '''The financial industry is undergoing a massive transformation with the widespread adoption of blockchain technology. Major banks and financial institutions are now implementing blockchain-based systems for faster, more secure transactions.

The new blockchain platform, called "SecureChain," processes transactions in seconds rather than days, while maintaining the highest levels of security. The technology eliminates the need for intermediaries, reducing costs and increasing transparency.

"Blockchain is not just about cryptocurrency anymore," explains financial analyst Mark Thompson. "It's revolutionizing how we think about trust and transactions in the digital age."

The platform has already processed over $1 trillion in transactions since its launch six months ago. Regulatory bodies worldwide are working to establish clear guidelines for blockchain adoption in traditional finance.

Experts predict that within the next five years, blockchain will become the standard for all major financial transactions, from international wire transfers to stock trading.''',
                'excerpt': 'Blockchain technology transforms finance with faster, more secure transactions, eliminating intermediaries and increasing transparency.',
                'category': 'Technology',
                'status': 'published'
            },
            {
                'title': 'Virtual Reality in Education',
                'content': '''Virtual Reality (VR) technology is revolutionizing the educational landscape, providing immersive learning experiences that were previously impossible. Schools and universities are increasingly adopting VR headsets to create interactive, three-dimensional learning environments.

The VR education platform, "EduVerse," allows students to explore historical events, travel to distant planets, and conduct virtual science experiments. The technology has shown remarkable results in improving student engagement and retention rates.

"Students are no longer passive observers; they're active participants in their learning journey," says Dr. Jennifer Martinez, educational technology specialist. "VR makes learning truly experiential."

The platform includes over 500 virtual field trips, interactive simulations, and collaborative learning spaces. Students can work together in virtual environments, regardless of their physical location.

Research shows that students using VR technology show 40% higher retention rates and 60% increased engagement compared to traditional learning methods. The technology is particularly effective for subjects like history, science, and geography.''',
                'excerpt': 'Virtual Reality transforms education with immersive learning experiences, improving student engagement and retention rates significantly.',
                'category': 'Technology',
                'status': 'published'
            },
            
            # Sports Articles (4)
            {
                'title': 'College Football Championship Results',
                'content': '''The 2024 College Football Championship was a thrilling event that kept fans on the edge of their seats until the final whistle. The championship game between the University of Alabama and Clemson University was a nail-biter that went into overtime.

Alabama's quarterback, John Smith, threw for 350 yards and 3 touchdowns, leading his team to a 28-21 victory. The game was tied 21-21 at the end of regulation, forcing the first overtime in championship history.

"This is the greatest moment of my life," said Smith after the game. "To win the championship in overtime is something I'll never forget."

The victory marks Alabama's 18th national championship, extending their record as the most successful college football program in history. Head coach Nick Saban praised his team's resilience and determination throughout the season.

Fans from both schools showed incredible sportsmanship, with many staying after the game to congratulate the winning team. The championship parade is scheduled for next week in Tuscaloosa.''',
                'excerpt': 'Alabama wins the 2024 College Football Championship in an overtime thriller against Clemson, securing their 18th national title.',
                'category': 'Sports',
                'status': 'published'
            },
            {
                'title': 'Basketball Team Wins State Championship',
                'content': '''The school's basketball team has achieved an incredible milestone by winning the state championship for the first time in school history. The team, led by senior captain Michael Johnson, defeated their rivals in a thrilling final game that went down to the wire.

The championship game was played in front of a packed arena, with fans from both schools creating an electric atmosphere. The final score was 78-75, with Johnson scoring the winning basket in the last seconds of the game.

"This victory is the result of years of hard work and dedication," said Coach Williams. "These players have shown what it means to be a team and to never give up."

The team's success has inspired younger students and brought the school community together. The championship trophy will be displayed in the school's trophy case, serving as a reminder of what can be achieved through teamwork and perseverance.

A celebration parade is planned for next week, and the team will be honored at the annual sports banquet.''',
                'excerpt': 'School basketball team wins first state championship in dramatic fashion, inspiring the entire school community.',
                'category': 'Sports',
                'status': 'published'
            },
            {
                'title': 'Swimming Team Breaks Records',
                'content': '''The school's swimming team has made history by breaking three state records at the regional swimming championships. The team's performance was nothing short of spectacular, with multiple swimmers achieving personal best times.

Sophomore Sarah Chen broke the 100-meter freestyle record with a time of 52.3 seconds, while the relay team set a new record in the 4x100 medley relay. The team's overall performance earned them second place in the regional championships.

"These records represent years of training and dedication," said Coach Rodriguez. "Our swimmers have shown incredible discipline and determination."

The team's success has attracted attention from college recruiters, with several universities expressing interest in the school's talented swimmers. The achievement has also inspired younger students to join the swimming program.

The school plans to upgrade the swimming facilities to support the growing interest in the sport and to help future teams achieve even greater success.''',
                'excerpt': 'Swimming team breaks three state records at regional championships, attracting college recruiters and inspiring future athletes.',
                'category': 'Sports',
                'status': 'published'
            },
            {
                'title': 'Track and Field Excellence',
                'content': '''The track and field team has demonstrated exceptional performance this season, with athletes qualifying for the national championships in multiple events. The team's success is a testament to the hard work and dedication of both the athletes and coaches.

Senior runner David Kim qualified for nationals in both the 800-meter and 1600-meter events, while the 4x400 relay team also secured their spot at the national competition. The team's overall performance has earned them recognition as one of the top programs in the state.

"Our success comes from a culture of excellence and mutual support," said Coach Thompson. "Every athlete on this team pushes themselves and their teammates to be better."

The team's achievements have brought pride to the school community and have inspired younger students to pursue track and field. The school has invested in new training equipment to support the growing program.

The national championships will be held next month, and the entire school community is rallying behind the team as they prepare for the biggest competition of their careers.''',
                'excerpt': 'Track and field team qualifies multiple athletes for nationals, showcasing excellence and inspiring the school community.',
                'category': 'Sports',
                'status': 'published'
            },
            
            # Education Articles (4)
            {
                'title': 'New Online Learning Platform Launched',
                'content': '''A revolutionary new online learning platform has been launched, promising to transform the way students access education. The platform, called "EduConnect," offers courses from top universities around the world at a fraction of the traditional cost.

EduConnect features interactive video lectures, real-time discussions with professors, and AI-powered personalized learning paths. The platform currently offers over 1,000 courses in various subjects including computer science, business, arts, and sciences.

"We believe education should be accessible to everyone," says Dr. Michael Chen, founder of EduConnect. "Our platform breaks down the barriers of traditional education by making quality courses available to students anywhere in the world."

The platform has already attracted over 50,000 students in its first month, with positive feedback about the quality of instruction and the flexibility of the learning format.

Universities partnering with EduConnect include MIT, Stanford, Harvard, and Oxford, among others. The platform also offers certification programs that are recognized by employers worldwide.''',
                'excerpt': 'EduConnect, a new online learning platform, launches with courses from top universities, making quality education accessible worldwide.',
                'category': 'Education',
                'status': 'published'
            },
            {
                'title': 'Revolutionary STEM Education Program Introduced',
                'content': '''A groundbreaking new STEM education program has been introduced in schools across the country, designed to prepare students for the future workforce. The program, called "Future Innovators," combines hands-on learning with cutting-edge technology to create an engaging educational experience.

The program focuses on Science, Technology, Engineering, and Mathematics (STEM) subjects, using project-based learning and real-world applications. Students work with 3D printers, robotics kits, and coding platforms to solve real problems.

"We're preparing students for jobs that don't even exist yet," says Dr. Emily Rodriguez, director of the Future Innovators program. "By giving them hands-on experience with technology and problem-solving skills, we're setting them up for success in any field."

The program has already shown impressive results, with participating students showing 40% improvement in critical thinking skills and 60% increase in interest in STEM careers. Schools implementing the program have also seen higher attendance rates and improved student engagement.

The program is funded by a combination of government grants and private donations, making it accessible to schools in both urban and rural areas. Plans are already underway to expand the program to more schools next year.''',
                'excerpt': 'Future Innovators STEM program transforms education with hands-on learning and technology integration, preparing students for future careers.',
                'category': 'Education',
                'status': 'published'
            },
            {
                'title': 'Mental Health Education Initiative',
                'content': '''A comprehensive mental health education initiative has been launched in schools nationwide, addressing the growing need for mental health awareness and support among students. The program, called "Mind Matters," provides students with tools and resources to understand and manage their mental health.

The initiative includes workshops on stress management, anxiety reduction techniques, and building resilience. Students learn about the importance of mental health and how to support their peers who may be struggling.

"Mental health is just as important as physical health," says Dr. Lisa Park, mental health coordinator. "We're teaching students that it's okay to ask for help and that taking care of their mental well-being is a sign of strength."

The program has received positive feedback from students, parents, and educators. Schools implementing the initiative have reported improved student well-being and a more supportive school environment.

The program also includes training for teachers and staff to recognize signs of mental health issues and provide appropriate support. Mental health professionals are available for individual counseling sessions when needed.''',
                'excerpt': 'Mind Matters initiative promotes mental health awareness in schools, providing students with tools for emotional well-being and resilience.',
                'category': 'Education',
                'status': 'published'
            },
            {
                'title': 'Digital Literacy Program Success',
                'content': '''A comprehensive digital literacy program has been successfully implemented across the school district, preparing students for the increasingly digital world. The program teaches essential skills including coding, digital citizenship, online safety, and media literacy.

Students learn to navigate the digital landscape responsibly, understand how to evaluate online information, and develop critical thinking skills for the digital age. The program also includes hands-on experience with various digital tools and platforms.

"Digital literacy is no longer optional; it's essential for success in today's world," says technology coordinator James Wilson. "We're preparing students to be responsible digital citizens and future innovators."

The program has shown remarkable results, with students demonstrating improved digital skills and increased confidence in using technology for learning and communication. Parents have also participated in workshops to support their children's digital education.

The success of the program has attracted attention from other school districts, with several implementing similar initiatives. The program continues to evolve with new technologies and changing digital landscapes.''',
                'excerpt': 'Digital literacy program equips students with essential skills for the digital age, preparing them for future success in technology-driven world.',
                'category': 'Education',
                'status': 'published'
            },
            
            # Health Articles (4)
            {
                'title': 'New Fitness Program for Students',
                'content': '''A comprehensive fitness program has been introduced to promote physical health and wellness among students. The program, called "Fit for Life," combines traditional physical education with modern fitness techniques and nutrition education.

The program includes personalized fitness plans, nutrition workshops, and mental health components. Students learn about the importance of regular exercise, healthy eating habits, and maintaining a balanced lifestyle.

"We're not just teaching students to exercise; we're teaching them to live healthy lives," says fitness coordinator Maria Santos. "The program addresses physical, mental, and emotional well-being."

The program has received enthusiastic response from students and parents alike. Participants have shown improvements in physical fitness, energy levels, and overall well-being. The program also includes family fitness events to encourage healthy habits at home.

The school has invested in new fitness equipment and facilities to support the program. Plans are underway to expand the program to include after-school fitness clubs and competitive sports teams.''',
                'excerpt': 'Fit for Life program promotes comprehensive health and wellness among students through personalized fitness plans and nutrition education.',
                'category': 'Health',
                'status': 'published'
            },
            {
                'title': 'Mental Health Awareness Campaign',
                'content': '''A school-wide mental health awareness campaign has been launched to destigmatize mental health issues and provide support for students. The campaign, called "It's Okay to Not Be Okay," encourages open conversations about mental health and emotional well-being.

The campaign includes workshops, guest speakers, and student-led initiatives to promote mental health awareness. Students learn about common mental health challenges, coping strategies, and how to support their peers.

"Mental health affects everyone, and we need to talk about it openly," says school counselor Dr. Robert Kim. "This campaign is about creating a supportive environment where students feel safe to seek help."

The campaign has been well-received by the school community, with increased awareness and understanding of mental health issues. The school has also established a peer support program where trained students can provide initial support to their classmates.

The success of the campaign has inspired other schools to implement similar initiatives. The program continues to evolve based on student feedback and changing needs.''',
                'excerpt': 'Mental health awareness campaign promotes open conversations about emotional well-being and provides support for students in need.',
                'category': 'Health',
                'status': 'published'
            },
            {
                'title': 'Nutrition Education Program',
                'content': '''A comprehensive nutrition education program has been implemented to teach students about healthy eating habits and food choices. The program, called "Smart Eating," combines classroom learning with hands-on cooking experiences and garden projects.

Students learn about nutrition science, food preparation, and the importance of making healthy food choices. The program includes visits to local farms, cooking classes, and nutrition workshops led by health professionals.

"Good nutrition is the foundation of good health," says nutritionist Dr. Amanda Chen. "We're teaching students to make informed decisions about what they eat and how it affects their bodies and minds."

The program has led to positive changes in student eating habits and increased awareness of nutrition. Many students have started bringing healthier lunches to school and have influenced their families to make better food choices.

The school has also established a community garden where students can grow their own vegetables and learn about sustainable food production. The garden serves as a living classroom for nutrition and environmental education.''',
                'excerpt': 'Smart Eating nutrition program educates students about healthy food choices through hands-on learning and practical cooking experiences.',
                'category': 'Health',
                'status': 'published'
            },
            {
                'title': 'Wellness Center Opens',
                'content': '''A state-of-the-art wellness center has opened on campus, providing comprehensive health services for students and staff. The center offers physical health services, mental health counseling, and wellness programs in a modern, welcoming environment.

The wellness center includes a medical clinic, counseling offices, fitness facilities, and relaxation spaces. Services are provided by qualified health professionals including nurses, counselors, and wellness coaches.

"The wellness center is a one-stop destination for all health and wellness needs," says center director Dr. Sarah Johnson. "We're committed to supporting the physical, mental, and emotional well-being of our school community."

The center has been well-received by students and staff, with many taking advantage of the available services. The facility also serves as a hub for health education and wellness programs.

The center's success has inspired other schools to consider similar facilities. Plans are already underway to expand services and add new programs based on community needs and feedback.''',
                'excerpt': 'New wellness center provides comprehensive health services and wellness programs for the entire school community.',
                'category': 'Health',
                'status': 'published'
            },
            
            # Achievements Articles (4)
            {
                'title': 'School Wins National Science Award',
                'content': '''The school has been awarded the prestigious National Science Award for its outstanding achievements in scientific research and innovation. The award recognizes the school's commitment to fostering a culture of curiosity and excellence among its students and faculty.

The award ceremony was held in the capital, with representatives from top educational institutions in attendance. The principal accepted the award on behalf of the school, highlighting the collaborative efforts of students, teachers, and staff.

"This achievement is a testament to our dedication to academic excellence and innovation," said the principal. "We are proud of our students and grateful for the support of our community."

The school plans to use the award funds to further enhance its science labs and support student-led research projects in the coming year.''',
                'excerpt': 'Our school receives the National Science Award for excellence in research and innovation.',
                'category': 'Achievements',
                'status': 'published'
            },
            {
                'title': 'Student Wins International Math Competition',
                'content': '''Senior student Alex Rodriguez has achieved an incredible milestone by winning the prestigious International Mathematics Competition. Alex competed against students from over 50 countries and emerged victorious after solving complex mathematical problems that challenged even the brightest minds.

The competition, held in Singapore, tested participants on advanced topics including calculus, number theory, and mathematical logic. Alex's innovative approach to problem-solving and deep understanding of mathematical concepts impressed the international panel of judges.

"This victory represents years of dedication and passion for mathematics," said Alex's math teacher, Dr. Patricia Lee. "Alex has shown that with hard work and determination, anything is possible."

The achievement has brought international recognition to the school and inspired other students to pursue excellence in mathematics. Alex has received scholarship offers from top universities worldwide and plans to study mathematics at the university level.

The school community celebrated Alex's achievement with a special assembly and recognition ceremony. The victory serves as a reminder of the school's commitment to academic excellence and student success.''',
                'excerpt': 'Senior student Alex Rodriguez wins International Mathematics Competition, bringing international recognition to the school.',
                'category': 'Achievements',
                'status': 'published'
            },
            {
                'title': 'Robotics Team Qualifies for World Championship',
                'content': '''The school's robotics team has achieved an extraordinary feat by qualifying for the World Robotics Championship. The team, consisting of six students, designed and built a robot that can perform complex tasks autonomously, earning them a spot in the international competition.

The team's robot, named "Innovator," demonstrated exceptional performance in regional and national competitions, solving engineering challenges with creativity and technical skill. The robot's innovative design and programming impressed judges and competitors alike.

"This achievement represents months of hard work, collaboration, and innovation," said team captain Sarah Kim. "We're excited to represent our school and country at the world championship."

The team's success has inspired younger students to join the robotics program and pursue careers in engineering and technology. The school has invested in additional robotics equipment to support the growing interest in the program.

The World Robotics Championship will be held next month, and the entire school community is supporting the team as they prepare for the biggest competition of their careers. The team hopes to bring home the world championship trophy.''',
                'excerpt': 'School robotics team qualifies for World Championship with innovative robot design, inspiring future engineers and technologists.',
                'category': 'Achievements',
                'status': 'published'
            },
            {
                'title': 'School Receives Blue Ribbon Award',
                'content': '''The school has been honored with the prestigious Blue Ribbon Award, recognizing its excellence in education and commitment to student success. The award is given to schools that demonstrate outstanding academic achievement and innovative educational practices.

The Blue Ribbon Award is the highest honor that can be bestowed upon a school by the Department of Education. The recognition is based on comprehensive evaluations of academic performance, teaching quality, and school leadership.

"This award validates our commitment to providing the best possible education for our students," said the principal. "It reflects the hard work and dedication of our entire school community."

The school's innovative programs, high academic standards, and supportive learning environment were key factors in receiving the award. The recognition has attracted attention from educators nationwide who want to learn from the school's successful practices.

The Blue Ribbon Award brings additional funding and resources to the school, which will be used to further enhance educational programs and facilities. The achievement serves as motivation to continue striving for excellence in education.''',
                'excerpt': 'School receives prestigious Blue Ribbon Award for excellence in education and innovative teaching practices.',
                'category': 'Achievements',
                'status': 'published'
            }
        ]

        for article_data in articles_data:
            category = next(cat for cat in categories if cat.name == article_data['category'])
            article, created = Article.objects.get_or_create(
                title=article_data['title'],
                defaults={
                    'slug': slugify(article_data['title']),
                    'content': article_data['content'],
                    'excerpt': article_data['excerpt'],
                    'category': category,
                    'author': user,
                    'status': article_data['status'],
                    'published_at': timezone.now() if article_data['status'] == 'published' else None
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created article: {article.title}'))

        self.stdout.write(self.style.SUCCESS('Sample data creation completed successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} categories and {len(articles_data)} articles')) 