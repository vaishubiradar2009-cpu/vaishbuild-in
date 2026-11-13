/**
 * ====================================================================
 * MediCare AI - Supabase PostgreSQL Migration Runner (Node.js)
 * File: scripts/migrate.js
 * Description: Applies supabase/migrations/001_initial_schema.sql to
 *              Supabase Cloud PostgreSQL using direct pg connection or
 *              service role credentials.
 * ====================================================================
 */

const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

const { Client } = require('pg');

async function runMigration() {
    console.log('====================================================');
    console.log('🏥 MediCare AI - Supabase Migration Runner');
    console.log('====================================================\n');

    const migrationFile = path.resolve(__dirname, '../supabase/migrations/001_initial_schema.sql');
    if (!fs.existsSync(migrationFile)) {
        console.error(`❌ Migration file not found at: ${migrationFile}`);
        process.exit(1);
    }

    const sqlContent = fs.readFileSync(migrationFile, 'utf8');
    console.log(`📄 Loaded migration file: 001_initial_schema.sql (${sqlContent.length} bytes)`);

    // Retrieve database connection credentials
    // Supabase provides PostgreSQL direct connection string in Project Settings -> Database -> Connection String (URI)
    const dbUrl = process.env.SUPABASE_DB_URL || process.env.DATABASE_URL;
    const supabaseUrl = process.env.SUPABASE_URL;
    const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

    if (!dbUrl && (!supabaseUrl || !serviceRoleKey)) {
        console.error('\n❌ Missing database connection credentials in .env file!');
        console.log('\nPlease configure your .env with either:');
        console.log('  1. SUPABASE_DB_URL=postgresql://postgres.[ref]:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres');
        console.log('     OR');
        console.log('  2. SUPABASE_URL=https://[ref].supabase.co');
        console.log('     SUPABASE_SERVICE_ROLE_KEY=your_service_role_secret_key\n');
        console.log('💡 TIP: You can also copy and paste "001_initial_schema.sql" directly into the');
        console.log('   Supabase Dashboard SQL Editor at: https://supabase.com/dashboard/project/_/sql\n');
        process.exit(1);
    }

    if (dbUrl) {
        console.log('🔌 Connecting to Supabase Cloud PostgreSQL via Connection String...');
        
        // Supabase cloud PostgreSQL requires SSL
        const client = new Client({
            connectionString: dbUrl,
            ssl: {
                rejectUnauthorized: false
            }
        });

        try {
            await client.connect();
            console.log('✅ Connected successfully to Supabase PostgreSQL database.');

            console.log('🚀 Executing initial schema migration and seed data...');
            const startTime = Date.now();
            await client.query(sqlContent);
            const duration = ((Date.now() - startTime) / 1000).toFixed(2);

            console.log(`\n🎉 Migration applied successfully in ${duration}s!`);

            // Verify tables created
            const res = await client.query(`
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            `);

            console.log('\n📊 Tables verified in public schema:');
            res.rows.forEach(row => {
                console.log(`   - ${row.table_name}`);
            });

            // Verify seed counts
            const docCount = await client.query('SELECT COUNT(*) FROM doctors');
            const articleCount = await client.query('SELECT COUNT(*) FROM health_articles');
            const emergencyCount = await client.query('SELECT COUNT(*) FROM emergency_contacts');
            
            console.log('\n🌱 Seed data verification:');
            console.log(`   - Doctors registered: ${docCount.rows[0].count}`);
            console.log(`   - Health articles: ${articleCount.rows[0].count}`);
            console.log(`   - Emergency helplines: ${emergencyCount.rows[0].count}`);

            await client.end();
            console.log('\n✨ Database setup complete. You can now start MediCare AI with `python app.py`!\n');
            process.exit(0);

        } catch (err) {
            console.error('\n❌ Migration failed during execution:');
            console.error(err.message);
            if (err.detail) console.error(`Detail: ${err.detail}`);
            if (err.hint) console.error(`Hint: ${err.hint}`);
            await client.end().catch(() => {});
            process.exit(1);
        }
    } else {
        // Fallback or instructions if user only gave SUPABASE_URL + SERVICE_ROLE_KEY
        console.log('ℹ️  SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY detected.');
        console.log('For raw DDL migrations (CREATE TABLE / RLS), Supabase recommends using the Postgres Connection Pooler.');
        console.log('Please add SUPABASE_DB_URL in your .env or run this script after setting SUPABASE_DB_URL.');
        console.log('Alternatively, paste the contents of supabase/migrations/001_initial_schema.sql into your Supabase SQL Editor.');
        process.exit(0);
    }
}

runMigration().catch(err => {
    console.error('Unexpected error:', err);
    process.exit(1);
});
