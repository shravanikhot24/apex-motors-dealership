const express = require('express');
const cors = require('cors');
const { MongoClient, ObjectId } = require('mongodb');
const app = express();
app.use(cors()); app.use(express.json());
const port = process.env.PORT || 5001;
const mongo = new MongoClient(process.env.MONGO_URL || 'mongodb://mongo:27017');
let db;
const seed = [
  {id:'dealer-kansas-city', full_name:'Apex Motors Kansas City', city:'Kansas City', state:'Kansas', address:'901 Main Street', phone:'(913) 555-0118', rating:4.8},
  {id:'dealer-wichita', full_name:'Apex Motors Wichita', city:'Wichita', state:'Kansas', address:'4800 East Kellogg', phone:'(316) 555-0182', rating:4.6},
  {id:'dealer-denver', full_name:'Apex Motors Denver', city:'Denver', state:'Colorado', address:'1450 Blake Street', phone:'(303) 555-0144', rating:4.7},
  {id:'dealer-austin', full_name:'Apex Motors Austin', city:'Austin', state:'Texas', address:'2201 South Congress', phone:'(512) 555-0190', rating:4.5}
];
async function init(){ await mongo.connect(); db=mongo.db(process.env.DB_NAME || 'test_database'); const dealers=db.collection('dealers'); if(await dealers.countDocuments()===0) await dealers.insertMany(seed); }
app.get('/health',(req,res)=>res.json({status:'ok',service:'dealer-service'}));
app.get('/dealers',async(req,res)=>{const query=req.query.state?{state:new RegExp(`^${req.query.state}$`,'i')}:{ }; res.json(await db.collection('dealers').find(query,{projection:{_id:0}}).toArray());});
app.get('/dealers/:id',async(req,res)=>{const dealer=await db.collection('dealers').findOne({id:req.params.id},{projection:{_id:0}}); if(!dealer)return res.status(404).json({error:'Dealer not found'}); dealer.reviews=await db.collection('reviews').find({dealer_id:req.params.id},{projection:{_id:0}}).sort({created_at:-1}).toArray(); res.json(dealer);});
app.get('/reviews',async(req,res)=>{const query=req.query.dealer_id?{dealer_id:req.query.dealer_id}:{}; res.json(await db.collection('reviews').find(query,{projection:{_id:0}}).sort({created_at:-1}).toArray());});
app.post('/reviews',async(req,res)=>{const data={dealer_id:req.body.dealer_id,user:req.body.user,comment:req.body.comment,rating:Number(req.body.rating||5),sentiment:req.body.sentiment,score:req.body.score,created_at:new Date().toISOString()}; if(!data.dealer_id||!data.comment)return res.status(400).json({error:'dealer_id and comment are required'}); await db.collection('reviews').insertOne(data); res.status(201).json(data);});
app.get('/makes',(req,res)=>res.json([{make:'Toyota',models:['Camry','RAV4','Tacoma']},{make:'Ford',models:['Mustang','F-150','Bronco']},{make:'Honda',models:['Civic','CR-V','Accord']},{make:'Tesla',models:['Model 3','Model Y','Model S']} ]));
init().then(()=>app.listen(port,()=>console.log(`dealer service listening on ${port}`))).catch(err=>{console.error(err);process.exit(1)});
